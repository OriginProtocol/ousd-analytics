import sys
from datetime import datetime
from decimal import Decimal
from django.conf import settings

from core.blockchain.addresses import (
    CHAINLINK_ORACLE,
    DAI,
    OGN,
    OGN_STAKING,
    OPEN_ORACLE,
    OUSD,
    STRATAAVEDAI,
    STRATCOMP,
    VAULT,
)
from core.etherscan import get_contract_transactions
from core.blockchain.const import (
    E_18,
    BLOCKS_PER_YEAR,
    ASSET_TICKERS,
    COMPOUND_FOR_SYMBOL,
    CONTRACT_FOR_SYMBOL,
    DECIMALS_FOR_SYMBOL,
    ETHERSCAN_CONTRACTS,
    LOG_CONTRACTS,
    START_OF_EVERYTHING,
)
from core.blockchain.decode import slot
from core.blockchain.rpc import (
    balanceOf,
    balanceOfUnderlying,
    borrowRatePerBlock,
    chainlink_ethUsdPrice,
    chainlink_tokEthPrice,
    # chainlink_tokUsdPrice,
    debug_trace_transaction,
    exchnageRateStored,
    get_block,
    get_transaction,
    get_transaction_receipt,
    ogn_staking_total_outstanding,
    open_oracle_price,
    ousd_rebasing_credits,
    ousd_non_rebasing_supply,
    priceUSDMint,
    priceUSDRedeem,
    rebasing_credits_per_token,
    request,
    strategyCheckBalance,
    supplyRatePerBlock,
    totalSupply,
    totalBorrows,
)
from core.blockchain.sigs import (
    DEPRECATED_SIG_EVENT_WITHDRAWN,
    DEPRECATED_SIG_EVENT_STAKED,
    SIG_EVENT_STAKED,
    SIG_EVENT_WITHDRAWN,
    TRANSFER,
)
from core.models import (
    AssetBlock,
    Block,
    CTokenSnapshot,
    DebugTx,
    EtherscanPointer,
    Log,
    LogPointer,
    OgnStaked,
    OgnStakingSnapshot,
    OracleSnapshot,
    OusdTransfer,
    SupplySnapshot,
    Transaction,
)


def build_asset_block(symbol, block_number):
    symbol = symbol.upper()
    compstrat_holding = Decimal(0)
    aavestrat_holding = Decimal(0)

    if block_number == "latest" or block_number > 11060000:
        if symbol == "USDC":
            compstrat_holding += balanceOfUnderlying(
                COMPOUND_FOR_SYMBOL[symbol],
                STRATCOMP,
                DECIMALS_FOR_SYMBOL[symbol],
                block_number,
            )
        elif symbol == "USDT":
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

    ora_tok_usd_min = (
        0 if symbol == "COMP" else priceUSDMint(VAULT, symbol, block_number)
    )
    ora_tok_usd_max = (
        0 if symbol == "COMP" else priceUSDRedeem(VAULT, symbol, block_number)
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
        threepoolstrat_holding=Decimal(0),
        aavestrat_holding=aavestrat_holding,
    )


def build_debug_tx(tx_hash):
    data = debug_trace_transaction(tx_hash)
    return DebugTx(tx_hash=tx_hash, block_number=0, data=data["result"])


def ensure_latest_logs(upto):
    pointers = {x.contract: x for x in LogPointer.objects.all()}
    for contract in LOG_CONTRACTS:
        pointer = None
        if contract not in pointers:
            pointer = LogPointer(contract=contract, last_block=START_OF_EVERYTHING)
            pointer.save()
        else:
            pointer = pointers[contract]
        start_block = pointer.last_block + 1
        while start_block <= upto:
            end_block = min(start_block + 1000, upto)
            download_logs_from_contract(contract, start_block, end_block)
            pointer.last_block = end_block
            pointer.save()
            start_block = pointer.last_block + 1


def ensure_all_transactions(block_number):
    """ Verify we have all transactions using Etherscan as a secondary source of
    transaction data.  This has the benefit of including failed transactions
    and transactions that do not generate logs.
    """
    pointers = {x.contract: x for x in EtherscanPointer.objects.all()}

    if settings.ETHERSCAN_API_KEY:

        for address in ETHERSCAN_CONTRACTS:
            if address not in pointers:
                pointers[address] = EtherscanPointer.objects.create(
                    contract=address,
                    last_block=0,
                )

            for tx in get_contract_transactions(
                address,
                pointers[address].last_block,
                block_number
            ):
                ensure_transaction_and_downstream(tx.get('hash'))

            pointers[address].last_block = block_number
            pointers[address].save()


def download_logs_from_contract(contract, start_block, end_block):
    print("D", contract, start_block, end_block)
    data = request(
        "eth_getLogs",
        [
            {
                "fromBlock": hex(start_block),
                "toBlock": hex(end_block),
                "address": contract,
            }
        ],
    )
    for tx_hash in set([x["transactionHash"] for x in data["result"]]):
        ensure_transaction_and_downstream(tx_hash)


def ensure_log_record(raw_log):
    block_number = int(raw_log["blockNumber"], 16)
    log_index = int(raw_log["logIndex"], 16)
    log = Log.objects.filter(
        block_number=block_number,
        transaction_hash=raw_log["transactionHash"],
        log_index=log_index,
    )
    if log:
        return log
    log = Log(
        address=raw_log["address"],
        block_number=block_number,
        log_index=log_index,
        transaction_hash=raw_log["transactionHash"],
        transaction_index=int(raw_log["transactionIndex"], 16),
        data=raw_log["data"],
        event_name="",
        topic_0="",
        topic_1="",
        topic_2="",
    )
    # This doesn't do anything?
    # if len(raw_log["data"]) >= 10:
    #     signature = raw_log["data"][0:10]
    if len(raw_log["topics"]) >= 1:
        log.topic_0 = raw_log["topics"][0]
    if len(raw_log["topics"]) >= 2:
        log.topic_1 = raw_log["topics"][1]
    if len(raw_log["topics"]) >= 3:
        log.topic_2 = raw_log["topics"][2]
    log.save()
    return log


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
        s.non_rebasing_credits = Decimal(0)
        s.credits = ousd_rebasing_credits(block_number) + s.non_rebasing_credits
        s.computed_supply = dai + usdt + usdc
        s.reported_supply = totalSupply(OUSD, 18, block_number)
        s.non_rebasing_supply = ousd_non_rebasing_supply(block_number)
        s.credits_ratio = s.computed_supply / s.credits
        s.rebasing_credits_ratio = (s.computed_supply - s.non_rebasing_supply) / (
            s.credits - s.non_rebasing_credits
        )
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


def ensure_asset(symbol, block_number):
    q = AssetBlock.objects.filter(symbol=symbol, block_number=block_number)
    if q.count():
        return q.first()
    else:
        ab = build_asset_block(symbol, block_number)
        ab.save()
        return ab


def ensure_block(block_number):
    blocks = list(Block.objects.filter(block_number=block_number))
    if len(blocks) > 0:
        return blocks[0]
    else:
        raw_block = get_block(block_number)
        block_time = datetime.utcfromtimestamp(int(raw_block["timestamp"], 16))
        block = Block(block_number=block_number, block_time=block_time)
        block.save()
        return block


def maybe_store_transfer_record(log, block):
    # Must be a transfer event
    if (
        log["topics"][0]
        != TRANSFER
    ):
        return None
    # Must be on OUSD
    if log["address"] != "0x2a8e1e676ec238d8a992307b495b45b3feaa5e86":
        return None
    tx_hash = log["transactionHash"]
    log_index = int(log["logIndex"], 16)
    db_transfer = list(
        OusdTransfer.objects.filter(tx_hash=tx_hash, log_index=log_index)
    )
    if len(db_transfer) > 0:
        return db_transfer[0]

    transfer = OusdTransfer(
        tx_hash_id=tx_hash,
        log_index=log_index,
        block_time=block.block_time,
        from_address="0x" + log["topics"][1][-40:],
        to_address="0x" + log["topics"][2][-40:],
        amount=int(slot(log["data"], 0), 16) / E_18,
    )
    transfer.save()
    return transfer


def maybe_store_stake_withdrawn_record(log, block):
    # Must be a Staked or Withdrawn event
    if (
        log["address"] != OGN_STAKING or
        log["topics"][0] not in [
            SIG_EVENT_STAKED,
            SIG_EVENT_WITHDRAWN,
            DEPRECATED_SIG_EVENT_STAKED,
            DEPRECATED_SIG_EVENT_WITHDRAWN,
        ]
    ):
        return None

    tx_hash = log["transactionHash"]
    log_index = int(log["logIndex"], 16)
    db_staked = list(
        OgnStaked.objects.filter(tx_hash=tx_hash, log_index=log_index)
    )
    if len(db_staked) > 0:
        return db_staked[0]

    is_updated_staked_event = log["topics"][0] == SIG_EVENT_STAKED
    is_withdrawn_event = log["topics"][0] == SIG_EVENT_WITHDRAWN
    is_staked_event = log["topics"][0] == DEPRECATED_SIG_EVENT_STAKED or is_updated_staked_event

    duration = 0
    rate = 0

    if is_updated_staked_event:
        # store duration in days
        duration = int(slot(log["data"], 1), 16) / (24 * 60 * 60)
        # convert rate back to yearly rate
        rate = Decimal(
            int(slot(log["data"], 2), 16) / E_18
        ) * 365 / Decimal(duration)

    staked = OgnStaked(
        tx_hash=tx_hash,
        log_index=log_index,
        block_time=block.block_time,
        user_address="0x" + log["topics"][1][-40:],
        is_staked=is_staked_event,
        amount=int(slot(log["data"], 0), 16) / 1e18,
        staked_amount=int(slot(log["data"], 1), 16) / 1e18 if is_withdrawn_event else 0,
        duration=duration,
        rate=rate
    )
    staked.save()
    return staked


def ensure_transaction_and_downstream(tx_hash):
    db_tx = list(Transaction.objects.filter(tx_hash=tx_hash))
    if len(db_tx) > 0:
        return db_tx[0]

    raw_transaction = get_transaction(tx_hash)
    receipt = get_transaction_receipt(tx_hash)
    debug = debug_trace_transaction(tx_hash)

    block_number = int(raw_transaction["blockNumber"], 16)
    block = ensure_block(block_number)

    transaction = Transaction(
        tx_hash=tx_hash,
        block_number=block_number,
        block_time=block.block_time,
        data=raw_transaction,
        receipt_data=receipt,
        debug_data=debug,
    )
    transaction.save()

    for log in receipt["logs"]:
        ensure_log_record(log)
        maybe_store_transfer_record(log, block)
        maybe_store_stake_withdrawn_record(log, block)

    return transaction


def ensure_ctoken_snapshot(underlying_symbol, block_number):
    ctoken_address = COMPOUND_FOR_SYMBOL.get(underlying_symbol)

    if not ctoken_address:
        print('ERROR: Unknown underlying asset for cToken', file=sys.stderr)
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

        s = CTokenSnapshot()
        s.block_number = block_number
        s.address = ctoken_address
        s.borrow_rate = borrow_rate
        s.borrow_apy = borrow_apy
        s.supply_rate = supply_rate
        s.supply_apy = supply_apy
        s.total_supply = totalSupply(ctoken_address, 8, block_number)
        s.total_borrows = totalBorrows(
            ctoken_address,
            underlying_decimals,
            block_number
        )
        s.exchange_rate_stored = exchnageRateStored(
            ctoken_address,
            block_number
        )
        s.save()

        return s
