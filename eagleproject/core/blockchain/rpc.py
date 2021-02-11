import os
import math
import json
import requests
from decimal import Decimal
from json.decoder import JSONDecodeError
from eth_abi import encode_single, decode_single
from eth_hash.auto import keccak
from eth_utils import encode_hex, decode_hex

from core.blockchain.addresses import (
    AAVE_LENDING_POOL_CORE_V1,
    CHAINLINK_ORACLE,
    CURVE_3POOL,
    OGN_STAKING,
    OPEN_ORACLE,
    OUSD,
)
from core.blockchain.const import (
    DECIMALS_FOR_SYMBOL,
    E_6,
    E_8,
    E_18,
    E_27,
    SYMBOL_FOR_CONTRACT,
    TRUE_256BIT,
)
from core.blockchain.decode import encode_args
from core.blockchain.sigs import (
    OPEN_ORACLE_PRICE,
    CHAINLINK_ETH_USD_PRICE,
    CHAINLINK_TOK_ETH_PRICE,
    CHAINLINK_TOK_USD_PRICE,
    SIG_FUNC_BORROW_RATE,
    SIG_FUNC_DURATION_REWARD_RATE,
    SIG_FUNC_EXCHANGE_RATE_STORED,
    SIG_FUNC_GET_CASH,
    SIG_FUNC_SUPPLY_RATE,
    SIG_FUNC_TOTAL_BORROWS,
    SIG_FUNC_TOTAL_RESERVES,
    SIG_FUNC_TOTAL_SUPPLY,
)
from core.logging import get_logger

log = get_logger(__name__)


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
            log.error(r.text)
        except Exception:
            pass
        raise err

    except Exception as err:
        log.error(err)
        raise err


def call(to, signature, payload, block="latest"):
    params = [
        {"to": to, "data": signature + payload},
        block if block == "latest" else hex(block),
    ]
    log.debug("RPC call params: {}".format(json.dumps(params)))
    return request("eth_call", params)


def call_by_sig(
        address,
        signature,
        args,
        block="latest") -> dict:
    """ Do an eth_call given a string function signature and an arg array """
    payload = encode_args(signature, args)
    sig_hash = encode_hex(keccak(signature.encode('utf-8')))[:10]
    return call(address, sig_hash, payload, block)


def call_and_return_wad(
        address,
        signature,
        args,
        block="latest") -> Decimal:
    """ Make an RPC call and return a "wad" value (18 decimals) """
    data = call_by_sig(address, signature, args, block)
    return Decimal(int(data["result"], 16)) / E_18


def call_and_return_ray(
        address,
        signature,
        args,
        block="latest") -> Decimal:
    """ Make an RPC call and return a "ray" value (27 decimals) """
    data = call_by_sig(address, signature, args, block)
    return Decimal(int(data["result"], 16)) / E_27


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


def getCash(coin_contract, decimals, block="latest"):
    signature = SIG_FUNC_GET_CASH[:10]
    payload = ""
    data = call(coin_contract, signature, payload, block)
    return Decimal(int(data["result"][0 : 64 + 2], 16)) / Decimal(
        math.pow(10, decimals)
    )


def exchangeRateStored(coin_contract, block="latest"):
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
        log.error("balanceOfUnderlying failed")
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
        log.error("strategyCheckBalance failed")
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


def staking_durationRewardRate(address, duration, block="latest"):
    """ SingleAssetStaking.durationRewardRate(uint256 _duration) """
    signature = SIG_FUNC_DURATION_REWARD_RATE[:10]
    payload = encode_single("(uint256)", [duration]).hex()
    data = call(address, signature, payload, block)
    return Decimal(int(data["result"], 16))


class AaveLendingPoolCore:
    """ LendingPoolCore calls """

    @staticmethod
    def isReserveBorrowingEnabled(address, block="latest") -> bool:
        data = call_by_sig(
            AAVE_LENDING_POOL_CORE_V1,
            "isReserveBorrowingEnabled(address)",
            [address],
            block
        )
        return data["result"] == TRUE_256BIT

    @staticmethod
    def getReserveAvailableLiquidity(address, decimals=18, block="latest") -> Decimal:
        return call_and_return_wad(
            AAVE_LENDING_POOL_CORE_V1,
            "getReserveAvailableLiquidity(address)",
            [address],
            block=block
        )

    @staticmethod
    def getReserveTotalBorrowsStable(address, decimals=18, block="latest") -> Decimal:
        return call_and_return_wad(
            AAVE_LENDING_POOL_CORE_V1,
            "getReserveTotalBorrowsStable(address)",
            [address],
            block=block
        )

    @staticmethod
    def getReserveTotalBorrowsVariable(address, block="latest") -> Decimal:
        return call_and_return_wad(
            AAVE_LENDING_POOL_CORE_V1,
            "getReserveTotalBorrowsVariable(address)",
            [address],
            block=block
        )

    @staticmethod
    def getReserveTotalLiquidity(address, block="latest") -> Decimal:
        return call_and_return_wad(
            AAVE_LENDING_POOL_CORE_V1,
            "getReserveTotalLiquidity(address)",
            [address],
            block=block
        )

    @staticmethod
    def getReserveCurrentLiquidityRate(address, block="latest") -> Decimal:
        # Return value is a "Ray" false decimal.  See: ds-math
        return call_and_return_ray(
            AAVE_LENDING_POOL_CORE_V1,
            "getReserveCurrentLiquidityRate(address)",
            [address],
            block=block
        )

    @staticmethod
    def getReserveCurrentVariableBorrowRate(address, block="latest") -> Decimal:
        # Return value is a "Ray" false decimal.  See: ds-math
        return call_and_return_ray(
            AAVE_LENDING_POOL_CORE_V1,
            "getReserveCurrentVariableBorrowRate(address)",
            [address],
            block=block
        )

    @staticmethod
    def getReserveCurrentStableBorrowRate(address, block="latest") -> Decimal:
        # Return value is a "Ray" false decimal.  See: ds-math
        return call_and_return_ray(
            AAVE_LENDING_POOL_CORE_V1,
            "getReserveCurrentStableBorrowRate(address)",
            [address],
            block=block
        )


class ThreePool:
    """ RPC Calls for Curve's 3pool """

    @staticmethod
    def coins(index, block="latest"):
        data = call_by_sig(CURVE_3POOL, "coins(uint256)", [index], block=block)
        result = data["result"]
        return decode_single("address", decode_hex(result))

    @staticmethod
    def get_all_coins(block="latest"):
        return [
            ThreePool.coins(0),
            ThreePool.coins(1),
            ThreePool.coins(2),
        ]

    @staticmethod
    def balances(index, block="latest"):
        data = call_by_sig(CURVE_3POOL, "balances(uint256)", [index], block)
        result = data["result"]
        return decode_single("uint256", decode_hex(result))

    @staticmethod
    def get_all_balances(block="latest"):
        coins = ThreePool.get_all_coins(block)

        retval = {}

        for i, coin in enumerate(coins):
            symbol = SYMBOL_FOR_CONTRACT[coin.lower()]
            decimals = DECIMALS_FOR_SYMBOL[symbol]
            retval[symbol] = Decimal(
                ThreePool.balances(i)
            ) / Decimal(
                math.pow(10, decimals)
            )

        return retval

    @staticmethod
    def initial_A(block="latest"):
        data = call_by_sig(CURVE_3POOL, "initial_A()", [], block)
        result = data["result"]
        return decode_single("uint256", decode_hex(result))

    @staticmethod
    def future_A(block="latest"):
        data = call_by_sig(CURVE_3POOL, "future_A()", [], block)
        result = data["result"]
        return decode_single("uint256", decode_hex(result))

    @staticmethod
    def initial_A_time(block="latest"):
        data = call_by_sig(CURVE_3POOL, "initial_A_time()", [], block)
        result = data["result"]
        return decode_single("uint256", decode_hex(result))

    @staticmethod
    def future_A_time(block="latest"):
        data = call_by_sig(CURVE_3POOL, "future_A_time()", [], block)
        result = data["result"]
        return decode_single("uint256", decode_hex(result))
