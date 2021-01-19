import os
import sys
import math
import requests
from decimal import Decimal
from json.decoder import JSONDecodeError
from eth_abi import encode_single

from core.blockchain.addresses import (
    CHAINLINK_ORACLE,
    OGN_STAKING,
    OPEN_ORACLE,
    OUSD,
)
from core.blockchain.const import E_6, E_8, E_18
from core.blockchain.sigs import (
    OPEN_ORACLE_PRICE,
    CHAINLINK_ETH_USD_PRICE,
    CHAINLINK_TOK_ETH_PRICE,
    CHAINLINK_TOK_USD_PRICE,
    SIG_FUNC_BORROW_RATE,
    SIG_FUNC_EXCHANGE_RATE_STORED,
    SIG_FUNC_SUPPLY_RATE,
    SIG_FUNC_TOTAL_BORROWS,
    SIG_FUNC_TOTAL_RESERVES,
    SIG_FUNC_TOTAL_SUPPLY,
)


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
    signature = SIG_FUNC_TOTAL_SUPPLY[:10]
    payload = ""
    data = call(coin_contract, signature, payload, block)
    return Decimal(int(data["result"][0 : 64 + 2], 16)) / Decimal(
        math.pow(10, decimals)
    )


def totalBorrows(coin_contract, decimals, block="latest"):
    signature = SIG_FUNC_TOTAL_BORROWS[:10]
    payload = ""
    data = call(coin_contract, signature, payload, block)
    return Decimal(int(data["result"][0 : 64 + 2], 16)) / Decimal(
        math.pow(10, decimals)
    )


def totalReserves(coin_contract, decimals, block="latest"):
    signature = SIG_FUNC_TOTAL_RESERVES[:10]
    payload = ""
    data = call(coin_contract, signature, payload, block)
    return Decimal(int(data["result"][0 : 64 + 2], 16)) / Decimal(
        math.pow(10, decimals)
    )


def exchnageRateStored(coin_contract, block="latest"):
    signature = SIG_FUNC_EXCHANGE_RATE_STORED[:10]
    payload = ""
    data = call(coin_contract, signature, payload, block)
    return Decimal(int(data["result"][0:64+2], 16)) / E_18


def borrowRatePerBlock(coin_contract, block="latest"):
    signature = SIG_FUNC_BORROW_RATE[:10]
    payload = ""
    data = call(coin_contract, signature, payload, block)
    return Decimal(int(data["result"][0:64+2], 16)) / E_18


def supplyRatePerBlock(coin_contract, block="latest"):
    signature = SIG_FUNC_SUPPLY_RATE[:10]
    payload = ""
    data = call(coin_contract, signature, payload, block)
    return Decimal(int(data["result"][0:64+2], 16)) / E_18


def open_oracle_price(ticker, block="latest"):
    signature = OPEN_ORACLE_PRICE[:10]
    payload = encode_single("(string)", [ticker]).hex()
    data = call(OPEN_ORACLE, signature, payload, block)
    # price() returns 6 decimals
    return Decimal(int(data["result"][0:64 + 2], 16)) / E_6


def chainlink_ethUsdPrice(block="latest"):
    signature = CHAINLINK_ETH_USD_PRICE[:10]
    payload = ""
    data = call(CHAINLINK_ORACLE, signature, payload, block)
    # tokEthPrice() returns an ETH-USD price with 6 decimals
    return Decimal(int(data["result"][0:64 + 2], 16)) / E_6


def chainlink_tokEthPrice(ticker, block="latest"):
    signature = CHAINLINK_TOK_ETH_PRICE[:10]
    payload = encode_single("(string)", [ticker]).hex()
    data = call(CHAINLINK_ORACLE, signature, payload, block)
    # tokEthPrice() returns an ETH price with 8 decimals for some reason...
    return Decimal(int(data["result"][0:64 + 2], 16)) / E_8


def chainlink_tokUsdPrice(ticker, block="latest"):
    signature = CHAINLINK_TOK_USD_PRICE[:10]
    payload = encode_single("(string)", [ticker]).hex()
    data = call(CHAINLINK_ORACLE, signature, payload, block)
    # tokEthPrice() returns an ETH price with 8 decimals for some reason...
    return Decimal(int(data["result"][0:64 + 2], 16)) / E_8


def balanceOfUnderlying(coin_contract, holder, decimals, block="latest"):
    signature = "0x3af9e669"
    try:
        payload = encode_single("(address)", [holder]).hex()
        data = call(coin_contract, signature, payload, block)
        return Decimal(int(data["result"][0 : 64 + 2], 16)) / Decimal(
            math.pow(10, decimals)
        )
    except Exception:
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
    except Exception:
        print("ERROR: strategyCheckBalance failed")
        return Decimal(0)


def rebasing_credits_per_token(block="latest"):
    signature = "0x6691cb3d"  # rebasingCreditsPerToken()
    data = call(OUSD, signature, "", block)
    return Decimal(int(data["result"][0 : 64 + 2], 16)) / E_18


def ousd_rebasing_credits(block="latest"):
    signature = "0x077f22b7"  # rebasingCredits()
    data = call(OUSD, signature, "", block)
    return Decimal(int(data["result"][0 : 64 + 2], 16)) / E_18


def ousd_non_rebasing_supply(block="latest"):
    signature = "0xe696393a"  # nonRebasingSupply()
    data = call(OUSD, signature, "", block)
    return Decimal(int(data["result"][0 : 64 + 2], 16)) / E_18


def ogn_staking_total_outstanding(block):
    data = storage_at(OGN_STAKING, 54, block)
    return Decimal(int(data["result"][0 : 64 + 2], 16)) / E_18


def priceUSDMint(coin_contract, symbol, block="latest"):
    signature = "0x686b37ca"  # priceUSDMint(string)
    payload = encode_single("(string)", [symbol]).hex()
    data = call(coin_contract, signature, payload, block)
    return Decimal(int(data["result"], 16)) / E_18


def priceUSDRedeem(coin_contract, symbol, block="latest"):
    signature = "0x29a903ec"  # priceUSDRedeem(string)
    payload = encode_single("(string)", [symbol]).hex()
    data = call(coin_contract, signature, payload, block)
    return Decimal(int(data["result"], 16)) / E_18
