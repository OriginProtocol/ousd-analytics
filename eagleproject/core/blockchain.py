import os
import sys
import math
import datetime
import requests
from decimal import Decimal
from json.decoder import JSONDecodeError
from eth_abi import encode_single
from django.conf import settings

from core.sigs import (
    CHAINLINK_ETH_USD_PRICE,
    CHAINLINK_TOK_ETH_PRICE,
    CHAINLINK_TOK_USD_PRICE,
    OPEN_ORACLE_PRICE,
    TRANSFER,
    SIG_EVENT_STAKED,
    SIG_EVENT_WITHDRAWN,
)
from core.models import (
    AssetBlock,
    Block,
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
from core.etherscan import get_contract_transactions

START_OF_EVERYTHING = 10884500

USDT = "0xdac17f958d2ee523a2206206994597c13d831ec7"
USDC = "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48"
DAI = "0x6b175474e89094c44da98b954eedeac495271d0f"
COMP = "0xc00e94cb662c3520282e6f5717214004a7f26888"
CDAI = "0x5d3a536e4d6dbd6114cc1ead35777bab948e3643"
CUSDC = "0x39aa39c021dfbae8fac545936693ac917d5e7563"
CUSDT = "0xf650c3d88d12db855b8bf7d11be6c55a4e07dcc9"
THREEPOOL = "0x6c3f90f043a72fa612cbac8115ee7e52bde6e490"

OUSD = "0x2a8e1e676ec238d8a992307b495b45b3feaa5e86"
VAULT = "0xe75d77b1865ae93c7eaa3040b038d7aa7bc02f70"
TIMELOCK = "0x52bebd3d7f37ec4284853fd5861ae71253a7f428"

OGN = "0x8207c1ffc5b6804f6024322ccf34f29c3541ae26"
OGN_STAKING = "0x501804b374ef06fa9c427476147ac09f1551b9a0"

STRATCOMP = "0xd5433168ed0b1f7714819646606db509d9d8ec1f"
STRATAAVEDAI = "0x051caefa90adf261b8e8200920c83778b7b176b6"

OUSD_USDT_UNISWAP = "0xcc01d9d54d06b6a0b6d09a9f79c3a6438e505f71"
OUSD_USDT_SUSHI = "0xe4455fdec181561e9ffe909dde46aaeaedc55283"
SNOWSWAP = "0x7c2fa8c30db09e8b3c147ac67947829447bf07bd"

# Oracles
MIX_ORACLE = "0x4d4f5e7a1fe57f5ceb38bfce8653effa5e584458"  # Meta oracle
OPEN_ORACLE = "0x922018674c12a7f0d394ebeef9b58f186cde13c1"  # Token prices
CHAINLINK_ORACLE = "0x8DE3Ac42F800a1186b6D70CB91e0D6876cC36759"  # Tokens

CHAINLINK_ETH_USD_FEED = "0x5f4eC3Df9cbd43714FE2740f5E3616155c5b8419"  # ETH
CHAINLINK_DAI_ETH_FEED = "0x773616E4d11A78F511299002da57A0a94577F1f4"
CHAINLINK_USDC_ETH_FEED = "0x986b5E1e1755e3C2440e960477f25201B0a8bbD4"
CHAINLINK_USDT_ETH_FEED = "0xEe9F2375b4bdF6387aa8265dD4FB8F16512A1d46"
# Not currently used?
# UNISWAP_ANCHORED_VIEW = "0x922018674c12a7f0d394ebeef9b58f186cde13c1"

CONTRACT_FOR_SYMBOL = {
    "DAI": DAI,
    "USDT": USDT,
    "USDC": USDC,
    "COMP": COMP,
}

DECIMALS_FOR_SYMBOL = {
    "COMP": 18,
    "DAI": 18,
    "USDT": 6,
    "USDC": 6,
}

THREEPOOLINDEX_FOR_ASSET = {
    DAI: 0,
    USDC: 1,
    USDT: 2,
}

COMPOUND_FOR_SYMBOL = {
    "DAI": CDAI,
    "USDT": CUSDT,
    "USDC": CUSDC,
}

LOG_CONTRACTS = [
    OUSD,
    VAULT,
    STRATCOMP,
    # STRATAAVEDAI,  # no events
    OUSD_USDT_UNISWAP,
    TIMELOCK,
    OGN_STAKING,
]
ETHERSCAN_CONTRACTS = [OUSD, VAULT, TIMELOCK]

ASSET_TICKERS = ["DAI", "USDC", "USDT"]


def request(method, params):
    url = os.environ.get("PROVIDER_URL")

    if url is None:
        raise Exception("No PROVIDER_URL ENV variable defined")

    params = {
        "jsonrpc": "2.0",
        "id": 0,
        "method": method,
        "params": params,
    }

    r = requests.post(url, json=params)

    try:
        return r.json()

    except JSONDecodeError as err:
        try:
            print(r.text, file=sys.stderr)
        except Exception:
            pass
        raise err

    except Exception as err:
        print(err, file=sys.stderr)
        raise err


def call(to, signature, payload, block="latest"):
    params = [
        {"to": to, "data": signature + payload},
        block if block == "latest" else hex(block),
    ]
    return request("eth_call", params)


def storage_at(address, slot, block="latest"):
    params = [address, hex(slot), block if block == "latest" else hex(block)]
    return request("eth_getStorageAt", params)


def debug_trace_transaction(tx_hash):
    params = [tx_hash]
    data = request("trace_transaction", params)
    return data.get("result", {})


def latest_block():
    data = request("eth_blockNumber", [])
    return int(data["result"], 16)


def get_block(block_number):
    hex_block = hex(block_number)
    params = [hex_block, False]
    data = request("eth_getBlockByNumber", params)
    return data["result"]


def get_transaction(tx_hash):
    data = request("eth_getTransactionByHash", [tx_hash])
    return data["result"]


def get_transaction_receipt(tx_hash):
    data = request("eth_getTransactionReceipt", [tx_hash])
    return data["result"]


def balanceOf(coin_contract, holder, decimals, block="latest"):
    signature = "0x70a08231"
    payload = encode_single("(address)", [holder]).hex()
    data = call(coin_contract, signature, payload, block)
    return Decimal(int(data["result"][0 : 64 + 2], 16)) / Decimal(
        math.pow(10, decimals)
    )


def totalSupply(coin_contract, decimals, block="latest"):
    signature = "0x18160ddd"
    payload = ""
    data = call(coin_contract, signature, payload, block)
    return Decimal(int(data["result"][0 : 64 + 2], 16)) / Decimal(
        math.pow(10, decimals)
    )


def open_oracle_price(ticker, block="latest"):
    signature = OPEN_ORACLE_PRICE[:10]
    payload = encode_single("(string)", [ticker]).hex()
    data = call(OPEN_ORACLE, signature, payload, block)
    # price() returns 6 decimals
    return Decimal(int(data["result"][0:64 + 2], 16)) / Decimal(1e6)


def chainlink_ethUsdPrice(block="latest"):
    signature = CHAINLINK_ETH_USD_PRICE[:10]
    payload = ""
    data = call(CHAINLINK_ORACLE, signature, payload, block)
    # tokEthPrice() returns an ETH-USD price with 6 decimals
    return Decimal(int(data["result"][0:64 + 2], 16)) / Decimal(1e6)


def chainlink_tokEthPrice(ticker, block="latest"):
    signature = CHAINLINK_TOK_ETH_PRICE[:10]
    payload = encode_single("(string)", [ticker]).hex()
    data = call(CHAINLINK_ORACLE, signature, payload, block)
    # tokEthPrice() returns an ETH price with 8 decimals for some reason...
    return Decimal(int(data["result"][0:64 + 2], 16)) / Decimal(1e8)


def chainlink_tokUsdPrice(ticker, block="latest"):
    signature = CHAINLINK_TOK_USD_PRICE[:10]
    payload = encode_single("(string)", [ticker]).hex()
    data = call(CHAINLINK_ORACLE, signature, payload, block)
    # tokEthPrice() returns an ETH price with 8 decimals for some reason...
    return Decimal(int(data["result"][0:64 + 2], 16)) / Decimal(1e8)


def balanceOfUnderlying(coin_contract, holder, decimals, block="latest"):
    signature = "0x3af9e669"
    try:
        payload = encode_single("(address)", [holder]).hex()
        data = call(coin_contract, signature, payload, block)
        return Decimal(int(data["result"][0 : 64 + 2], 16)) / Decimal(
            math.pow(10, decimals)
        )
    except:
        print("ERROR: balanceOfUnderlying failed")
        return Decimal(0)


def strategyCheckBalance(strategy, coin_contract, decimals, block="latest"):
    signature = "0x5f515226"
    try:
        payload = encode_single("(address)", [coin_contract]).hex()
        data = call(strategy, signature, payload, block)
        return Decimal(int(data["result"][0 : 64 + 2], 16)) / Decimal(
            math.pow(10, decimals)
        )
    except:
        print("ERROR: strategyCheckBalance failed")
        return Decimal(0)


def rebasing_credits_per_token(block="latest"):
    signature = "0x6691cb3d"  # rebasingCreditsPerToken()
    data = call(OUSD, signature, "", block)
    return Decimal(int(data["result"][0 : 64 + 2], 16)) / Decimal(math.pow(10, 18))


def ousd_rebasing_credits(block="latest"):
    signature = "0x077f22b7"  # rebasingCredits()
    data = call(OUSD, signature, "", block)
    return Decimal(int(data["result"][0 : 64 + 2], 16)) / Decimal(math.pow(10, 18))


def ousd_non_rebasing_supply(block="latest"):
    signature = "0xe696393a"  # nonRebasingSupply()
    data = call(OUSD, signature, "", block)
    return Decimal(int(data["result"][0 : 64 + 2], 16)) / Decimal(math.pow(10, 18))


def ogn_staking_total_outstanding(block):
    data = storage_at(OGN_STAKING, 54, block)
    return Decimal(int(data["result"][0 : 64 + 2], 16)) / Decimal(1e18)


def priceUSDMint(coin_contract, symbol, block="latest"):
    signature = "0x686b37ca"  # priceUSDMint(string)
    payload = encode_single("(string)", [symbol]).hex()
    data = call(coin_contract, signature, payload, block)
    return Decimal(int(data["result"], 16)) / Decimal(1e18)


def priceUSDRedeem(coin_contract, symbol, block="latest"):
    signature = "0x29a903ec"  # priceUSDRedeem(string)
    payload = encode_single("(string)", [symbol]).hex()
    data = call(coin_contract, signature, payload, block)
    return Decimal(int(data["result"], 16)) / Decimal(1e18)


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
    if len(raw_log["data"]) >= 10:
        signature = raw_log["data"][0:10]
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
        block_time = datetime.datetime.utcfromtimestamp(int(raw_block["timestamp"], 16))
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
        amount=int(_slot(log["data"], 0), 16) / 1e18,
    )
    transfer.save()
    return transfer


def maybe_store_stake_withdrawn_record(log, block):
    # Must be a Staked or Withdrawn event
    if (
        log["address"] != OGN_STAKING or
        (
            log["address"] == OGN_STAKING and
            log["topics"][0] not in [SIG_EVENT_STAKED, SIG_EVENT_WITHDRAWN]
        )
    ):
        return None

    tx_hash = log["transactionHash"]
    log_index = int(log["logIndex"], 16)
    db_staked = list(
        OgnStaked.objects.filter(tx_hash=tx_hash, log_index=log_index)
    )
    if len(db_staked) > 0:
        return db_staked[0]

    staked = OgnStaked(
        tx_hash=tx_hash,
        log_index=log_index,
        block_time=block.block_time,
        user_address="0x" + log["topics"][1][-40:],
        is_staked=log["topics"][0] == SIG_EVENT_STAKED,
        amount=int(_slot(log["data"], 0), 16) / 1e18,
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


def _slot(value, i):
    """Get the x 256bit field from a data string"""
    return value[2 + i * 64 : 2 + (i + 1) * 64]
