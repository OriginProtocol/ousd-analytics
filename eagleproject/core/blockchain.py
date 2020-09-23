import requests
import math
from decimal import Decimal
from eth_abi import encode_single

from core.models import AssetBlock, DebugTx, LogPointer, Log

START_OF_EVERYTHING = 10884500

USDT = "0xdac17f958d2ee523a2206206994597c13d831ec7"
USDC = "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48"
DAI = "0x6b175474e89094c44da98b954eedeac495271d0f"
CDAI = "0x5d3a536e4d6dbd6114cc1ead35777bab948e3643"
CUSDC = "0x39aa39c021dfbae8fac545936693ac917d5e7563"
CUSDT = "0xf650c3d88d12db855b8bf7d11be6c55a4e07dcc9"
OUSD = "0x2a8e1e676ec238d8a992307b495b45b3feaa5e86"
VAULT = "0x277e80f3e14e7fb3fc40a9d6184088e0241034bd"
COMPSTRAT = "0x47211b1d1f6da45aaee06f877266e072cf8baa74"
OUSD_USDT_UNISWAP = "0xcc01d9d54d06b6a0b6d09a9f79c3a6438e505f71"

CONTRACT_FOR_SYMBOL = {
    "DAI": DAI,
    "USDT": USDT,
    "USDC": USDC,
}

DECIMALS_FOR_SYMBOL = {
    "DAI": 18,
    "USDT": 6,
    "USDC": 6,
}

COMPOUND_FOR_SYMBOL = {
    "DAI": CDAI,
    "USDT": CUSDT,
    "USDC": CUSDC,
}

LOG_CONTRACTS = [OUSD, VAULT, COMPSTRAT, OUSD_USDT_UNISWAP]


def request(method, params):
    url = "https://eth-mainnet.alchemyapi.io/v2/PGQ2MsXpNvo48XeXC7_ML8WFRmrK2hl5"
    params = {
        "jsonrpc": "2.0",
        "id": 0,
        "method": method,
        "params": params,
    }
    r = requests.post(url, json=params)
    return r.json()


def call(to, signature, payload, block="latest"):
    params = [
        {"to": to, "data": signature + payload},
        block if block == "latest" else hex(block),
    ]
    return request("eth_call", params)


def debug_trace_transaction(tx_hash):
    params = [tx_hash]
    return request("trace_transaction", params)


def lastest_block():
    data = request("eth_blockNumber", [])
    return int(data["result"], 16)


def balanceOf(coin_contract, holder, decimals, block="latest"):
    signature = "0x70a08231"
    payload = encode_single("(address)", [holder]).hex()
    data = call(coin_contract, signature, payload, block)
    return Decimal(int(data["result"][0 : 64 + 2], 16)) / Decimal(
        math.pow(10, decimals)
    )


def balanceOfUnderlying(coin_contract, holder, decimals, block="latest"):
    signature = "0x3af9e669"
    try:
        payload = encode_single("(address)", [holder]).hex()
        data = call(coin_contract, signature, payload, block)
        return Decimal(int(data["result"][0 : 64 + 2], 16)) / Decimal(
            math.pow(10, decimals)
        )
    except:
        print("EXPLODY")
        return Decimal(0)


def priceUSDMint(coin_contract, symbol, block="latest"):
    signature = "0x686b37ca"
    payload = encode_single("(string)", [symbol]).hex()
    data = call(coin_contract, signature, payload, block)
    return Decimal(int(data["result"], 16)) / Decimal(1e18)


def priceUSDRedeem(coin_contract, symbol, block="latest"):
    signature = "0x29a903ec"
    payload = encode_single("(string)", [symbol]).hex()
    data = call(coin_contract, signature, payload, block)
    return Decimal(int(data["result"], 16)) / Decimal(1e18)


def build_asset_block(symbol, block_number):
    symbol = symbol.upper()
    return AssetBlock(
        symbol=symbol,
        block_number=block_number,
        ora_tok_usd_min=priceUSDMint(VAULT, symbol),
        ora_tok_usd_max=priceUSDRedeem(VAULT, symbol),
        vault_holding=balanceOf(
            CONTRACT_FOR_SYMBOL[symbol], VAULT, DECIMALS_FOR_SYMBOL[symbol]
        ),
        compstrat_holding=balanceOfUnderlying(
            COMPOUND_FOR_SYMBOL[symbol], COMPSTRAT, DECIMALS_FOR_SYMBOL[symbol]
        ),
    )


def build_debug_tx(tx_hash):
    data = debug_trace_transaction(tx_hash)
    return DebugTx(tx_hash=tx_hash, block_number=0, data=data["result"])


def ensure_latest_logs(upto):
    pointers = {x.contract: x for x in LogPointer.objects.all()}
    for contract in LOG_CONTRACTS:
        if not contract in pointers:
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
    for raw_log in data['result']:
        ensure_log_record(raw_log)


def ensure_log_record(raw_log):
    block_number = int(raw_log['blockNumber'],16)
    log_index =  int(raw_log['logIndex'],16)
    log = Log.objects.filter(block_number=block_number, log_index=log_index)
    if log:
        return log
    log = Log(
        address = raw_log['address'],
        block_number=block_number,
        log_index=log_index,
        transaction_hash=raw_log['transactionHash'],
        transaction_index=int(raw_log['transactionIndex'],16),
        data = raw_log['data'],
        event_name="",
        topic_0="",
        topic_1="",
        topic_2="",
        )
    if len(raw_log['data']) >= 10:
        signature = raw_log['data'][0:10]
    if len(raw_log['topics'])>=1:
        log.topic_0 = raw_log['topics'][0]
    if len(raw_log['topics'])>=2:
        log.topic_1 = raw_log['topics'][1]
    if len(raw_log['topics'])>=3:
        log.topic_2 = raw_log['topics'][2]
    log.save()
    return log

    