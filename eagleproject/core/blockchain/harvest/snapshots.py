from decimal import Decimal
from datetime import datetime, timezone

from core.blockchain.addresses import (
    CHAINLINK_ORACLE,
    CURVE_METAPOOL,
    DAI,
    FLIPPER,
    OGN,
    OGN_STAKING,
    OPEN_ORACLE,
    OUSD,
    OUSD_USDT_UNISWAP_V3,
    STORY_STAKING_VAULT,
    STRATAAVEDAI,
    STRATAAVE2,
    STRATCOMP1,
    STRATCOMP2,
    STRAT3POOL,
    STRATCONVEX1,
    OUSD_VAULT,
    OETH_VAULT,
    OETH,
    OETH_CURVE_AMO_STRATEGY,
    OETH_ETH_AMO_METAPOOL,
)
from core.blockchain.const import (
    BLOCKS_PER_YEAR,
    ASSET_TICKERS,
    COMPOUND_FOR_SYMBOL,
    CONTRACT_FOR_SYMBOL,
    DECIMALS_FOR_SYMBOL,
    VAULT_FEE_UPGRADE_BLOCK,
)
from core.blockchain.rpc import (
    AaveLendingPoolCore,
    OUSDMetaStrategy,
    LUSDMetaStrategy,
    ThreePoolStrat,
    ThreePool,
    balanceOf,
    balanceOfUnderlying,
    borrowRatePerBlock,
    chainlink_ethUsdPrice,
    chainlink_tokEthPrice,
    exchangeRateStored,
    get_balance,
    getCash,
    getPendingRewards,
    ogn_staking_total_outstanding,
    open_oracle_price,
    origin_token_rebasing_credits,
    origin_token_non_rebasing_supply,
    priceUnitMint,
    priceUnitRedeem,
    rebasing_credits_per_token,
    strategyCheckBalance,
    story_staking_total_supply,
    story_staking_claiming_index,
    story_staking_staking_index,
    supplyRatePerBlock,
    totalSupply,
    totalBorrows,
    totalReserves,
    OUSDMetaPool,
    LUSDMetaPool,
    OETHCurveAMOStrategy,
)
from core.logging import get_logger
from core.models import (
    AssetBlock,
    AaveLendingPoolCoreSnapshot,
    CTokenSnapshot,
    OgnStaked,
    OgnStakingSnapshot,
    OracleSnapshot,
    StoryStake,
    StoryStakingSnapshot,
    SupplySnapshot,
    ThreePoolSnapshot,
    OriginTokens
)

from core.blockchain.strategies import OUSD_STRATEGIES, OUSD_BACKING_ASSETS
from core.blockchain.strategies import OETH_STRATEGIES, OETH_BACKING_ASSETS

from django.core.exceptions import ObjectDoesNotExist

logger = get_logger(__name__)


def isbetween(start, end, v):
    if not isinstance(v, int):
        return False
    if v < start:
        return False
    if v > end:
        return False
    return True

def _build_asset_block_oeth(symbol, block_number):
    strat_holdings = {}

    # TODO: Rename these columns??
    ora_tok_usd_min = 0
    ora_tok_usd_max = 0
    if symbol == "ETH":
        ora_tok_usd_max = 1
        ora_tok_usd_min = 1
    elif symbol != "OETH":
        try:
            ora_tok_usd_min = priceUnitMint(OETH_VAULT, CONTRACT_FOR_SYMBOL[symbol], block_number)
        except:
            print("Failed to fetch price from OETH oracle for {}".format(symbol))

        try:
            ora_tok_usd_max = priceUnitRedeem(OETH_VAULT, CONTRACT_FOR_SYMBOL[symbol], block_number)
        except:
            print("Failed to fetch price from OETH oracle for {}".format(symbol))

    for (strat_key, strat) in OETH_STRATEGIES.items():
        if strat.get("HARDCODED", False) == True:
            # Ignore hardcoded contracts
            continue
        elif block_number != "latest" and block_number <= strat.get("FROM_BLOCK", 0):
            # Fetch events only after the specific block, if configured
            continue
        if symbol not in strat.get("SUPPORTED_ASSETS", OETH_BACKING_ASSETS):
            # Unsupported asset
            continue

        holding = 0

        if strat_key == "oeth_curve_amo":
            holding = OETHCurveAMOStrategy.get_underlying_balance(block_number).get(symbol, Decimal(0))
        else:
            holding = strategyCheckBalance(
                strat.get("ADDRESS"),
                CONTRACT_FOR_SYMBOL[symbol],
                DECIMALS_FOR_SYMBOL[symbol],
                block_number,
            )

        strat_holdings[strat_key] = str(holding)

    vault_balance = balanceOf(
        CONTRACT_FOR_SYMBOL[symbol],
        OETH_VAULT,
        DECIMALS_FOR_SYMBOL[symbol],
        block_number,
    ) if symbol != "ETH" else get_balance(OETH_VAULT, block_number)

    return AssetBlock(
        project=OriginTokens.OETH,
        symbol=symbol,
        block_number=block_number,
        ora_tok_usd_min=ora_tok_usd_min,
        ora_tok_usd_max=ora_tok_usd_max,
        vault_holding=vault_balance,
        strat_holdings=strat_holdings,
        # Not used for OETH
        compstrat_holding=Decimal(0),
        threepoolstrat_holding=Decimal(0),
        aavestrat_holding=Decimal(0),
    )


def build_asset_block(symbol, block_number, project = OriginTokens.OUSD):
    symbol = symbol.upper()

    if project == OriginTokens.OETH:
        return _build_asset_block_oeth(symbol, block_number)

    compstrat_holding = Decimal(0)
    aavestrat_holding = Decimal(0)
    threepoolstrat_holding = Decimal(0)
    strat_holdings = {}

    # Compound Strats
    if isbetween(11060000, 13399969, block_number):
        if symbol in ["USDC", "USDT", "DAI"]:
            compstrat_holding += balanceOfUnderlying(
                COMPOUND_FOR_SYMBOL[symbol],
                STRATCOMP1,
                DECIMALS_FOR_SYMBOL[symbol],
                block_number,
            )
        elif symbol == "COMP":
            compstrat_holding += balanceOf(
                CONTRACT_FOR_SYMBOL[symbol],
                STRATCOMP1,
                DECIMALS_FOR_SYMBOL[symbol],
                block_number,
            )
    if block_number == "latest" or block_number > 13399969:
        if symbol in ["USDC", "USDT", "DAI"]:
            compstrat_holding += balanceOfUnderlying(
                COMPOUND_FOR_SYMBOL[symbol],
                STRATCOMP2,
                DECIMALS_FOR_SYMBOL[symbol],
                block_number,
            )
        elif symbol == "COMP":
            compstrat_holding += balanceOf(
                CONTRACT_FOR_SYMBOL[symbol],
                STRATCOMP2,
                DECIMALS_FOR_SYMBOL[symbol],
                block_number,
            )

    # AAVE Strats
    if block_number < 11096410:
        pass
    elif block_number < 13399969:
        if symbol == "DAI":
            aavestrat_holding += strategyCheckBalance(
                STRATAAVEDAI,
                DAI,
                DECIMALS_FOR_SYMBOL[symbol],
                block_number,
            )
    elif block_number < 14040716:
        if symbol in ["DAI"]:
            aavestrat_holding += strategyCheckBalance(
                STRATAAVE2,
                CONTRACT_FOR_SYMBOL[symbol],
                DECIMALS_FOR_SYMBOL[symbol],
                block_number,
            )
    elif block_number < 14398806:
        if symbol in ["DAI", "USDT"]:
            aavestrat_holding += strategyCheckBalance(
                STRATAAVE2,
                CONTRACT_FOR_SYMBOL[symbol],
                DECIMALS_FOR_SYMBOL[symbol],
                block_number,
            )
    else:
        if symbol in ["DAI", "USDT", "USDC"]:
            aavestrat_holding += strategyCheckBalance(
                STRATAAVE2,
                CONTRACT_FOR_SYMBOL[symbol],
                DECIMALS_FOR_SYMBOL[symbol],
                block_number,
            )

    # 3pool
    if (
        block_number == "latest"
        or block_number > 13677000
        and symbol in ("USDC", "USDT", "DAI")
    ):
        threepoolstrat_holding += ThreePoolStrat.get_underlying_balance(block_number).get(symbol)
    elif block_number > 11831747 and symbol in ("USDC", "USDT", "DAI"):
        threepoolstrat_holding += strategyCheckBalance(
            STRAT3POOL,
            CONTRACT_FOR_SYMBOL[symbol],
            DECIMALS_FOR_SYMBOL[symbol],
            block_number,
        )

    ora_tok_usd_min = 0 if symbol == "COMP" else -1
    ora_tok_usd_max = 0 if symbol == "COMP" else -1

    if ora_tok_usd_min < 0:
        try:
            ora_tok_usd_min = (
                priceUnitMint(OUSD_VAULT, CONTRACT_FOR_SYMBOL[symbol], block_number)
                if symbol in OUSD_BACKING_ASSETS
                else 0
            )
        except:
            print("Failed to fetch price from OUSD oracle for {}".format(symbol))
 
    if ora_tok_usd_max < 0:
        try:
            ora_tok_usd_max = (
                priceUnitRedeem(OUSD_VAULT, CONTRACT_FOR_SYMBOL[symbol], block_number)
                if symbol in OUSD_BACKING_ASSETS
                else 0
            )
        except:
            print("Failed to fetch price from OUSD oracle for {}".format(symbol))


    for (strat_key, strat) in OUSD_STRATEGIES.items():
        if strat.get("HARDCODED", False) == True:
            # Ignore hardcoded contracts
            continue
        if block_number != "latest" and block_number <= strat.get("FROM_BLOCK", 0):
            # Fetch events only after the specific block, if configured
            continue
        if symbol not in strat.get("SUPPORTED_ASSETS", OUSD_BACKING_ASSETS):
            # Unsupported asset
            continue

        holding = Decimal(0)

        if strat.get("IS_COMPOUND_COMPATIBLE", False) and symbol == "COMP":
            holding = getPendingRewards(
                strat.get("ADDRESS"),
                DECIMALS_FOR_SYMBOL[symbol],
                block_number,
            )
        elif strat_key == "ousd_metastrat":
            holding += OUSDMetaStrategy.get_underlying_balance(block_number).get(symbol)
        elif strat_key == "lusd_metastrat":
            holding += LUSDMetaStrategy.get_underlying_balance(block_number).get(symbol)
        else:
            holding = strategyCheckBalance(
                strat.get("ADDRESS"),
                CONTRACT_FOR_SYMBOL[symbol],
                DECIMALS_FOR_SYMBOL[symbol],
                block_number,
            )

        strat_holdings[strat_key] = str(holding)

    return AssetBlock(
        project=project,
        symbol=symbol,
        block_number=block_number,
        ora_tok_usd_min=ora_tok_usd_min,
        ora_tok_usd_max=ora_tok_usd_max,
        vault_holding=balanceOf(
            CONTRACT_FOR_SYMBOL[symbol],
            OUSD_VAULT,
            DECIMALS_FOR_SYMBOL[symbol],
            block_number,
        ),
        compstrat_holding=compstrat_holding,
        threepoolstrat_holding=threepoolstrat_holding,
        aavestrat_holding=aavestrat_holding,
        strat_holdings=strat_holdings,
    )


def ensure_asset(symbol, block_number, project=OriginTokens.OUSD):
    try:
        ab = AssetBlock.objects.filter(symbol=symbol, block_number=block_number, project=project).first()
        if ab is not None:
            return ab
    except ObjectDoesNotExist:
        pass
    ab = build_asset_block(symbol, block_number, project)
    ab.save()
    return ab


def ensure_supply_snapshot(block_number, project=OriginTokens.OUSD) -> SupplySnapshot:
    try:
        s = SupplySnapshot.objects.filter(block_number=block_number,project=project).first()
        if s is not None:
            return s
    except ObjectDoesNotExist:
        pass

    s = SupplySnapshot()
    s.project = project
    s.block_number = block_number

    s.non_rebasing_credits = Decimal(0)  # No longer used in contract

    if project == OriginTokens.OUSD:
        # TODO: Should we use `redeem_value` for OUSD as well?
        dai = ensure_asset("DAI", block_number).total()
        usdt = ensure_asset("USDT", block_number).total()
        usdc = ensure_asset("USDC", block_number).total()
        ousd = ensure_asset("OUSD", block_number).total()
        lusd = ensure_asset("LUSD", block_number).total()

        s.credits = origin_token_rebasing_credits(block_number) + s.non_rebasing_credits

        s.computed_supply = dai + usdt + usdc + ousd + lusd
        s.reported_supply = totalSupply(OUSD, 18, block_number)
        s.non_rebasing_supply = origin_token_non_rebasing_supply(block_number)
        s.credits_ratio = s.computed_supply / s.credits
        fee_bps = Decimal(0.1)
        if block_number > VAULT_FEE_UPGRADE_BLOCK:
            fee_bps = Decimal(0.2)
        future_fee = (s.computed_supply - s.reported_supply) * fee_bps
        next_rebase_supply = (
            s.computed_supply - s.non_rebasing_supply - future_fee
        )
        s.rebasing_credits_ratio = next_rebase_supply / s.credits
        s.rebasing_credits_per_token = rebasing_credits_per_token(block_number)
        ousd_amo_supply = OUSDMetaStrategy.get_underlying_balance().get("OUSD", Decimal(0))
        s.non_rebasing_boost_multiplier = (s.computed_supply - ousd_amo_supply) / (s.computed_supply - s.non_rebasing_supply)
    else:
        eth = ensure_asset("ETH", block_number, OriginTokens.OETH).redeem_value()
        weth = ensure_asset("WETH", block_number, OriginTokens.OETH).redeem_value()
        frxeth = ensure_asset("FRXETH", block_number, OriginTokens.OETH).redeem_value()
        reth = ensure_asset("RETH", block_number, OriginTokens.OETH).redeem_value()
        steth = ensure_asset("STETH", block_number, OriginTokens.OETH).redeem_value()
        oeth = ensure_asset("OETH", block_number, OriginTokens.OETH).redeem_value()

        s.credits = origin_token_rebasing_credits(block_number, contract=OETH) + s.non_rebasing_credits

        s.computed_supply = oeth + steth + reth + frxeth + weth + eth
        s.reported_supply = totalSupply(OETH, 18, block_number)
        s.non_rebasing_supply = origin_token_non_rebasing_supply(block_number, contract=OETH)
        if s.computed_supply == 0 and s.credits == 0:
            s.credits_ratio = 0
        else:
            s.credits_ratio = s.computed_supply / s.credits

        future_fee = (s.computed_supply - s.reported_supply) * Decimal(0.2)
        next_rebase_supply = (
            s.computed_supply - s.non_rebasing_supply - future_fee
        )
        if next_rebase_supply == 0 and s.credits == 0:
            s.rebasing_credits_ratio = 0
        else:
            s.rebasing_credits_ratio = next_rebase_supply / s.credits
        s.rebasing_credits_per_token = rebasing_credits_per_token(block_number, contract=OETH)
        oeth_amo_supply = OETHCurveAMOStrategy.get_underlying_balance().get("OETH", Decimal(0))
        s.non_rebasing_boost_multiplier = (s.computed_supply - oeth_amo_supply) / (s.computed_supply - s.non_rebasing_supply)

    s.save()
    return s


def ensure_staking_snapshot(block_number):
    try:
        s = OgnStakingSnapshot.objects.get(block_number=block_number)
        if s is not None:
            return s
    except ObjectDoesNotExist:
        pass

    ogn_balance = balanceOf(OGN, OGN_STAKING, 18, block=block_number)
    total_outstanding = ogn_staking_total_outstanding(block_number)
    user_count = OgnStaked.objects.values("user_address").distinct().count()

    params = {
        "ogn_balance": ogn_balance,
        "total_outstanding": total_outstanding,
        "user_count": user_count,
    }

    tx, created = OgnStakingSnapshot.objects.get_or_create(
        block_number=block_number,
        defaults=params
    )

    if not created:
        tx.conditional_update(**params)

    return tx


def ensure_story_staking_snapshot(block_number):
    try:
        s = StoryStakingSnapshot.objects.get(block_number=block_number)
        if s is not None:
            return s
    except ObjectDoesNotExist:
        pass

    total_supply = story_staking_total_supply(block_number)
    claiming_index = story_staking_claiming_index(block_number)
    staking_index = story_staking_staking_index(block_number)
    vault_eth = get_balance(STORY_STAKING_VAULT, block_number)
    vault_ogn = balanceOf(
        OGN,
        STORY_STAKING_VAULT,
        18,
        block_number,
    )
    user_count = StoryStake.objects.values("user_address").distinct().count()

    return StoryStakingSnapshot.objects.create(
        block_number=block_number,
        total_supply=total_supply,
        claiming_index=claiming_index,
        staking_index=staking_index,
        vault_eth=vault_eth,
        vault_ogn=vault_ogn,
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
                price=usd_eth_price,
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
                    price=eth_price,
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
                    price=usd_price,
                )
            )


def ensure_ctoken_snapshot(underlying_symbol, block_number):
    ctoken_address = COMPOUND_FOR_SYMBOL.get(underlying_symbol)

    if not ctoken_address:
        logger.error("Unknown underlying asset for cToken")
        return None

    underlying_decimals = DECIMALS_FOR_SYMBOL[underlying_symbol]

    q = CTokenSnapshot.objects.filter(
        address=ctoken_address, block_number=block_number
    )

    if q.count():
        return q.first()

    else:
        borrow_rate = borrowRatePerBlock(ctoken_address, block_number)
        supply_rate = supplyRatePerBlock(ctoken_address, block_number)

        borrow_apy = borrow_rate * Decimal(BLOCKS_PER_YEAR)
        supply_apy = supply_rate * Decimal(BLOCKS_PER_YEAR)

        total_supply = totalSupply(ctoken_address, 8, block_number)
        exchange_rate_stored = exchangeRateStored(ctoken_address, block_number)

        s = CTokenSnapshot()
        s.block_number = block_number
        s.address = ctoken_address
        s.borrow_rate = borrow_rate
        s.borrow_apy = borrow_apy
        s.supply_rate = supply_rate
        s.supply_apy = supply_apy
        s.total_supply = total_supply
        s.total_borrows = totalBorrows(
            ctoken_address, underlying_decimals, block_number
        )
        s.total_cash = getCash(
            ctoken_address, underlying_decimals, block_number
        )
        s.total_reserves = totalReserves(
            ctoken_address, underlying_decimals, block_number
        )
        s.exchange_rate_stored = exchange_rate_stored
        s.save()

        return s


def ensure_aave_snapshot(underlying_symbol, block_number):
    """ Get a snapshot of the Aave LendingPoolCore reserve for an asset """
    asset_address = CONTRACT_FOR_SYMBOL.get(underlying_symbol)

    if not asset_address:
        logger.error("Unknown underlying asset for Aave snapshot")
        return None

    q = AaveLendingPoolCoreSnapshot.objects.filter(
        asset=asset_address, block_number=block_number
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
        s.available_liquidity = (
            AaveLendingPoolCore.getReserveAvailableLiquidity(asset_address)
        )
        s.total_borrows_stable = (
            AaveLendingPoolCore.getReserveTotalBorrowsStable(asset_address)
        )
        s.total_borrows_variable = (
            AaveLendingPoolCore.getReserveTotalBorrowsVariable(asset_address)
        )
        s.total_liquidity = AaveLendingPoolCore.getReserveTotalLiquidity(
            asset_address
        )
        s.current_liquidity_rate = (
            AaveLendingPoolCore.getReserveCurrentLiquidityRate(asset_address)
        )
        s.variable_borrow_rate = (
            AaveLendingPoolCore.getReserveCurrentVariableBorrowRate(
                asset_address
            )
        )
        s.stable_borrow_rate = (
            AaveLendingPoolCore.getReserveCurrentStableBorrowRate(asset_address)
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
            ThreePool.initial_A_time(block_number), tz=timezone.utc
        )
        s.future_a_time = datetime.fromtimestamp(
            ThreePool.future_A_time(block_number), tz=timezone.utc
        )
        s.save()

        return s


def latest_snapshot(project=OriginTokens.OUSD):
    return SupplySnapshot.objects.filter(project=project).order_by("-block_number")[0]


def snapshot_at_block(block, project=OriginTokens.OUSD):
    return SupplySnapshot.objects.filter(block_number__lte=block,project=project).order_by(
        "-block_number"
    ).first()


def latest_snapshot_block_number(project=OriginTokens.OUSD):
    return latest_snapshot(project=project).block_number


def calculate_ousd_snapshot_data(block=None):
    project = OriginTokens.OUSD
    pools_config = [
        ("Curve", CURVE_METAPOOL, False),
        ("Uniswap v3 OUSD/USDT", OUSD_USDT_UNISWAP_V3, False),
        ("OUSD Swap", FLIPPER, True),
    ]
    pools = []
    totals_by_rebasing = {True: Decimal(0), False: Decimal(0)}
    for name, address, is_rebasing in pools_config:
        amount = balanceOf(
            OUSD, address, 18, "latest" if block is None else block
        )
        pools.append(
            {
                "name": name,
                "amount": amount,
                "is_rebasing": is_rebasing,
            }
        )
        totals_by_rebasing[is_rebasing] += amount
    pools = sorted(pools, key=lambda pool: 0 - pool["amount"])

    snapshot = latest_snapshot(project=project) if block is None else snapshot_at_block(block, project=project)
    other_rebasing = (
        snapshot.rebasing_reported_supply() - totals_by_rebasing[True]
    )
    other_non_rebasing = (
        snapshot.non_rebasing_reported_supply() - totals_by_rebasing[False]
    )

    return [
        pools,
        totals_by_rebasing,
        other_rebasing,
        other_non_rebasing,
        snapshot,
    ]

def calculate_oeth_snapshot_data(block=None):
    project = OriginTokens.OETH
    pools_config = [
        ("Curve", OETH_ETH_AMO_METAPOOL),
    ]
    pools = []
    totals_by_rebasing = {True: Decimal(0), False: Decimal(0)}
    for name, address in pools_config:
        amount = balanceOf(
            OETH, address, 18, "latest" if block is None else block
        )
        pools.append(
            {
                "name": name,
                "amount": amount,
                "is_rebasing": False,
            }
        )
        totals_by_rebasing[True] += amount
    pools = sorted(pools, key=lambda pool: 0 - pool["amount"])

    snapshot = latest_snapshot(project=project) if block is None else snapshot_at_block(block, project=project)
    other_rebasing = (
        snapshot.rebasing_reported_supply() - totals_by_rebasing[True]
    )
    other_non_rebasing = (
        snapshot.non_rebasing_reported_supply() - totals_by_rebasing[False]
    )

    return [
        pools,
        totals_by_rebasing,
        other_rebasing,
        other_non_rebasing,
        snapshot,
    ]
