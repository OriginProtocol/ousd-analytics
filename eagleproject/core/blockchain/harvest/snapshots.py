from decimal import Decimal
from datetime import datetime, timezone

from core.blockchain.addresses import (
    CHAINLINK_ORACLE,
    DAI,
    OGN,
    OGN_STAKING,
    OPEN_ORACLE,
    OUSD,
    STRATAAVEDAI,
    STRATCOMP,
    STRAT3POOL,
    VAULT,
)
from core.blockchain.const import (
    BLOCKS_PER_YEAR,
    ASSET_TICKERS,
    COMPOUND_FOR_SYMBOL,
    CONTRACT_FOR_SYMBOL,
    DECIMALS_FOR_SYMBOL,
)
from core.blockchain.rpc import (
    AaveLendingPoolCore,
    ThreePool,
    balanceOf,
    balanceOfUnderlying,
    borrowRatePerBlock,
    chainlink_ethUsdPrice,
    chainlink_tokEthPrice,
    exchangeRateStored,
    getCash,
    ogn_staking_total_outstanding,
    open_oracle_price,
    ousd_rebasing_credits,
    ousd_non_rebasing_supply,
    priceUSDMint,
    priceUSDRedeem,
    rebasing_credits_per_token,
    strategyCheckBalance,
    supplyRatePerBlock,
    totalSupply,
    totalBorrows,
    totalReserves,
)
from core.logging import get_logger
from core.models import (
    AssetBlock,
    AaveLendingPoolCoreSnapshot,
    CTokenSnapshot,
    OgnStaked,
    OgnStakingSnapshot,
    OracleSnapshot,
    SupplySnapshot,
    ThreePoolSnapshot,
)

logger = get_logger(__name__)


def build_asset_block(symbol, block_number):
    symbol = symbol.upper()
    compstrat_holding = Decimal(0)
    aavestrat_holding = Decimal(0)
    threepoolstrat_holding = Decimal(0)

    if block_number == "latest" or block_number > 11060000:
        if symbol in ["USDC", "USDT", "DAI"]:
            compstrat_holding += balanceOfUnderlying(
                COMPOUND_FOR_SYMBOL[symbol],
                STRATCOMP,
                DECIMALS_FOR_SYMBOL[symbol],
                block_number,
            )
        elif symbol == "COMP":
            compstrat_holding += balanceOf(
                CONTRACT_FOR_SYMBOL[symbol],
                STRATCOMP,
                DECIMALS_FOR_SYMBOL[symbol],
                block_number,
            )

    # First AAVE Strat
    if block_number == "latest" or block_number >= 11096410:
        if symbol == "DAI":
            aavestrat_holding += strategyCheckBalance(
                STRATAAVEDAI,
                DAI,
                DECIMALS_FOR_SYMBOL[symbol],
                block_number,
            )

    # 3pool
    if (
        block_number == "latest"
        or block_number > 11831747
        and symbol in ("USDC", "USDT", "DAI")
    ):
        threepoolstrat_holding += strategyCheckBalance(
            STRAT3POOL,
            CONTRACT_FOR_SYMBOL[symbol],
            DECIMALS_FOR_SYMBOL[symbol],
            block_number,
        )

    ora_tok_usd_min = (
        0 if symbol == "COMP" else priceUSDMint(
            VAULT,
            CONTRACT_FOR_SYMBOL[symbol],
            block_number
        )
    )
    ora_tok_usd_max = (
        0 if symbol == "COMP" else priceUSDRedeem(
            VAULT,
            CONTRACT_FOR_SYMBOL[symbol],
            block_number
        )
    )

    return AssetBlock(
        symbol=symbol,
        block_number=block_number,
        ora_tok_usd_min=ora_tok_usd_min,
        ora_tok_usd_max=ora_tok_usd_max,
        vault_holding=balanceOf(
            CONTRACT_FOR_SYMBOL[symbol],
            VAULT,
            DECIMALS_FOR_SYMBOL[symbol],
            block_number,
        ),
        compstrat_holding=compstrat_holding,
        threepoolstrat_holding=threepoolstrat_holding,
        aavestrat_holding=aavestrat_holding,
    )


def ensure_asset(symbol, block_number):
    q = AssetBlock.objects.filter(symbol=symbol, block_number=block_number)
    if q.count():
        return q.first()
    else:
        ab = build_asset_block(symbol, block_number)
        ab.save()
        return ab


def ensure_supply_snapshot(block_number):
    q = SupplySnapshot.objects.filter(block_number=block_number)
    if q.count():
        return q.first()
    else:
        dai = ensure_asset("DAI", block_number).total()
        usdt = ensure_asset("USDT", block_number).total()
        usdc = ensure_asset("USDC", block_number).total()

        s = SupplySnapshot()
        s.block_number = block_number
        s.non_rebasing_credits = Decimal(0)  # No longer used in contract
        s.credits = ousd_rebasing_credits(block_number) + s.non_rebasing_credits
        s.computed_supply = dai + usdt + usdc
        s.reported_supply = totalSupply(OUSD, 18, block_number)
        s.non_rebasing_supply = ousd_non_rebasing_supply(block_number)
        s.credits_ratio = s.computed_supply / s.credits
        future_fee = (s.computed_supply - s.reported_supply) * Decimal(0.1)
        next_rebase_supply = s.computed_supply - s.non_rebasing_supply - future_fee
        s.rebasing_credits_ratio = next_rebase_supply / s.credits
        s.rebasing_credits_per_token = rebasing_credits_per_token(block_number)
        s.save()
        return s


def ensure_staking_snapshot(block_number):
    try:
        return OgnStakingSnapshot.objects.get(block_number=block_number)
    except OgnStakingSnapshot.DoesNotExist:
        pass

    ogn_balance = balanceOf(OGN, OGN_STAKING, 18, block=block_number)
    total_outstanding = ogn_staking_total_outstanding(block_number)
    user_count = OgnStaked.objects.values('user_address').distinct().count()

    return OgnStakingSnapshot.objects.create(
        block_number=block_number,
        ogn_balance=ogn_balance,
        total_outstanding=total_outstanding,
        user_count=user_count,
    )


def ensure_oracle_snapshot(block_number):
    """ Take oracle snapshots """
    existing_snaps = OracleSnapshot.objects.filter(block_number=block_number)
    if len(existing_snaps) > 0:
        return existing_snaps

    snaps = []

    # USD price of ETH
    usd_eth_price = chainlink_ethUsdPrice()
    if usd_eth_price:
        snaps.append(
            OracleSnapshot.objects.create(
                block_number=block_number,
                oracle=CHAINLINK_ORACLE,
                ticker_left="ETH",
                ticker_right="USD",
                price=usd_eth_price
            )
        )

    # Get oracle prices for all OUSD minting assets
    for ticker in ASSET_TICKERS:
        # ETH price
        eth_price = chainlink_tokEthPrice(ticker)
        if eth_price:
            snaps.append(
                OracleSnapshot.objects.create(
                    block_number=block_number,
                    oracle=CHAINLINK_ORACLE,
                    ticker_left=ticker,
                    ticker_right="ETH",
                    price=eth_price
                )
            )

        # USD price
        # Doesn't currently work?  reverts: "Price is not direct to usd"
        # usd_price = chainlink_tokUsdPrice(ticker)
        # if usd_price:
        #     snaps.append(
        #         OracleSnapshot.objects.create(
        #             block_number=block_number,
        #             oracle=CHAINLINK_ORACLE,
        #             ticker_left=ticker,
        #             ticker_right="USD",
        #             price=usd_price
        #         )
        #     )

        # Open Oracle
        usd_price = open_oracle_price(ticker)
        if usd_price:
            snaps.append(
                OracleSnapshot.objects.create(
                    block_number=block_number,
                    oracle=OPEN_ORACLE,
                    ticker_left=ticker,
                    ticker_right="USD",
                    price=usd_price
                )
            )


def ensure_ctoken_snapshot(underlying_symbol, block_number):
    ctoken_address = COMPOUND_FOR_SYMBOL.get(underlying_symbol)

    if not ctoken_address:
        logger.error('Unknown underlying asset for cToken')
        return None

    underlying_decimals = DECIMALS_FOR_SYMBOL[underlying_symbol]

    q = CTokenSnapshot.objects.filter(
        address=ctoken_address,
        block_number=block_number
    )

    if q.count():
        return q.first()

    else:
        borrow_rate = borrowRatePerBlock(ctoken_address, block_number)
        supply_rate = supplyRatePerBlock(ctoken_address, block_number)

        borrow_apy = borrow_rate * Decimal(BLOCKS_PER_YEAR)
        supply_apy = supply_rate * Decimal(BLOCKS_PER_YEAR)

        total_supply = totalSupply(ctoken_address, 8, block_number)
        exchange_rate_stored = exchangeRateStored(
            ctoken_address,
            block_number
        )

        s = CTokenSnapshot()
        s.block_number = block_number
        s.address = ctoken_address
        s.borrow_rate = borrow_rate
        s.borrow_apy = borrow_apy
        s.supply_rate = supply_rate
        s.supply_apy = supply_apy
        s.total_supply = total_supply
        s.total_borrows = totalBorrows(
            ctoken_address,
            underlying_decimals,
            block_number
        )
        s.total_cash = getCash(
            ctoken_address,
            underlying_decimals,
            block_number
        )
        s.total_reserves = totalReserves(
            ctoken_address,
            underlying_decimals,
            block_number
        )
        s.exchange_rate_stored = exchange_rate_stored
        s.save()

        return s


def ensure_aave_snapshot(underlying_symbol, block_number):
    """ Get a snapshot of the Aave LendingPoolCore reserve for an asset """
    asset_address = CONTRACT_FOR_SYMBOL.get(underlying_symbol)

    if not asset_address:
        logger.error('Unknown underlying asset for Aave snapshot')
        return None

    q = AaveLendingPoolCoreSnapshot.objects.filter(
        asset=asset_address,
        block_number=block_number
    )

    if q.count():
        return q.first()

    else:

        s = AaveLendingPoolCoreSnapshot()
        s.block_number = block_number
        s.asset = asset_address
        s.borrowing_enabled = AaveLendingPoolCore.isReserveBorrowingEnabled(
            asset_address
        )
        s.available_liquidity = AaveLendingPoolCore.getReserveAvailableLiquidity(
            asset_address
        )
        s.total_borrows_stable = AaveLendingPoolCore.getReserveTotalBorrowsStable(
            asset_address
        )
        s.total_borrows_variable = AaveLendingPoolCore.getReserveTotalBorrowsVariable(
            asset_address
        )
        s.total_liquidity = AaveLendingPoolCore.getReserveTotalLiquidity(
            asset_address
        )
        s.current_liquidity_rate = AaveLendingPoolCore.getReserveCurrentLiquidityRate(
            asset_address
        )
        s.variable_borrow_rate = AaveLendingPoolCore.getReserveCurrentVariableBorrowRate(
            asset_address
        )
        s.stable_borrow_rate = AaveLendingPoolCore.getReserveCurrentStableBorrowRate(
            asset_address
        )
        s.save()

        return s


def ensure_3pool_snapshot(block_number):
    """ Get a snapshot of 3pool """

    try:
        return ThreePoolSnapshot.objects.get(block_number=block_number)

    except ThreePoolSnapshot.DoesNotExist:
        balances = ThreePool.get_all_balances(block_number)

        s = ThreePoolSnapshot()
        s.block_number = block_number
        s.dai_balance = balances.get("DAI")
        s.usdc_balance = balances.get("USDC")
        s.usdt_balance = balances.get("USDT")
        s.initial_a = ThreePool.initial_A(block_number)
        s.future_a = ThreePool.future_A(block_number)
        s.initial_a_time = datetime.fromtimestamp(
            ThreePool.initial_A_time(block_number),
            tz=timezone.utc
        )
        s.future_a_time = datetime.fromtimestamp(
            ThreePool.future_A_time(block_number),
            tz=timezone.utc
        )
        s.save()

        return s
