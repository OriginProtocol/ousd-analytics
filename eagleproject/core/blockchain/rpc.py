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
    DRIPPER,
    OGN_STAKING,
    OPEN_ORACLE,
    OUSD,
    STORY_STAKING_SERIES,
    STRATCONVEX1,
    OUSD_METASTRAT,
    LUSD_METASTRAT,
    CURVE_METAPOOL,
    LUSD_METAPOOL,
    CVX_3POOL_REWARDS_POOL,
    CVX_OUSD_REWARDS_POOL,
    CVX_LUSD_REWARDS_POOL,
    DAI,
    USDT,
    USDC,
    OETH,
    OETH_CURVE_AMO_STRATEGY,
    OETH_ETH_AMO_METAPOOL,
    OETH_CURVE_AMO_REWARDS_POOL
)
from core.blockchain.const import (
    DECIMALS_FOR_SYMBOL,
    E_6,
    E_8,
    E_18,
    E_27,
    SYMBOL_FOR_CONTRACT,
    CONTRACT_FOR_SYMBOL,
    TRUE_256BIT,
)
from core.blockchain.decode import encode_args
from core.blockchain.sigs import (
    OPEN_ORACLE_PRICE,
    CHAINLINK_ETH_USD_PRICE,
    CHAINLINK_TOK_ETH_PRICE,
    CHAINLINK_TOK_USD_PRICE,
    SIG_DRIPPER_AVAILABLE_FUNDS,
    SIG_DRIPPER_CONFIG,
    SIG_FUNC_BORROW_RATE,
    SIG_FUNC_CURRENT_CLAIMING_INDEX,
    SIG_FUNC_CURRENT_STAKING_INDEX,
    SIG_FUNC_DURATION_REWARD_RATE,
    SIG_FUNC_EXCHANGE_RATE_STORED,
    SIG_FUNC_GET_CASH,
    SIG_FUNC_PRICE_USD_MINT,
    SIG_FUNC_PRICE_USD_REDEEM,
    SIG_FUNC_PRICE_UNIT_MINT,
    SIG_FUNC_PRICE_UNIT_REDEEM,
    SIG_FUNC_SUPPLY_RATE,
    SIG_FUNC_TOTAL_BORROWS,
    SIG_FUNC_TOTAL_RESERVES,
    SIG_FUNC_TOTAL_SUPPLY,
)
from core.logging import get_logger

from core.models import OriginTokens

log = get_logger(__name__)


class RPCError(Exception):
    def __init__(self, code, message):
        self.code = code
        self.message = message

    def __str__(self):
        return self.message

    def __repr__(self):
        return self.message


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


def get_balance(address, block="latest") -> Decimal:
    data = request("eth_getBalance", [address, hex(block)])
    return Decimal(int(data["result"], 16)) / E_18


def call(to, signature, payload, block="latest"):
    params = [
        {"to": to, "data": signature + payload},
        block if block == "latest" else hex(block),
    ]
    log.debug("RPC call params: {}".format(json.dumps(params)))
    return request("eth_call", params)


def call_by_sig(address, signature, args, block="latest") -> dict:
    """ Do an eth_call given a string function signature and an arg array """
    payload = encode_args(signature, args)
    sig_hash = encode_hex(keccak(signature.encode("utf-8")))[:10]
    return call(address, sig_hash, payload, block)


def call_and_return_wad(address, signature, args, block="latest") -> Decimal:
    """ Make an RPC call and return a "wad" value (18 decimals) """
    data = call_by_sig(address, signature, args, block)
    return Decimal(int(data["result"], 16)) / E_18


def call_and_return_ray(address, signature, args, block="latest") -> Decimal:
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


def creditsBalanceOf(holder, block="latest", project=OriginTokens.OUSD):
    token_addr = OUSD  if project == OriginTokens.OUSD else OETH
    signature = encode_hex(keccak(b"creditsBalanceOf(address)"))[:10]
    payload = encode_single("(address)", [holder]).hex()
    data = call(token_addr, signature, payload, block)

    return (
        Decimal(int(data["result"][0 : 64 + 2], 16))
        / Decimal(math.pow(10, 18)),
        Decimal(int(data["result"][64 + 2 : 2 * 64 + 2], 16))
        / Decimal(math.pow(10, 18)),
    )


def balanceOf(coin_contract, holder, decimals, block="latest"):
    signature = "0x70a08231"
    payload = encode_single("(address)", [holder]).hex()
    data = call(coin_contract, signature, payload, block)
    # this can happen if not live yet
    try:
        number = data["result"][0 : 64 + 2]
    except KeyError:
        return Decimal(0)
    if number == "0x":
        number = "0x0000000000000000000000000000000000000000000000000000000000000000"
    return Decimal(int(number, 16)) / Decimal(
        math.pow(10, decimals)
    )


def totalSupply(coin_contract, decimals, block="latest"):
    signature = SIG_FUNC_TOTAL_SUPPLY[:10]
    payload = ""
    data = call(coin_contract, signature, payload, block)
    # this can happen if not live yet
    try:
        number = data["result"][0 : 64 + 2]
    except KeyError:
        return Decimal(0)
    if number == "0x":
        number = "0x0000000000000000000000000000000000000000000000000000000000000000"
    return Decimal(int(number, 16)) / Decimal(
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
    return Decimal(int(data["result"][0 : 64 + 2], 16)) / E_18


def borrowRatePerBlock(coin_contract, block="latest"):
    signature = SIG_FUNC_BORROW_RATE[:10]
    payload = ""
    data = call(coin_contract, signature, payload, block)
    return Decimal(int(data["result"][0 : 64 + 2], 16)) / E_18


def supplyRatePerBlock(coin_contract, block="latest"):
    signature = SIG_FUNC_SUPPLY_RATE[:10]
    payload = ""
    data = call(coin_contract, signature, payload, block)
    return Decimal(int(data["result"][0 : 64 + 2], 16)) / E_18


def open_oracle_price(ticker, block="latest"):
    signature = OPEN_ORACLE_PRICE[:10]
    payload = encode_single("(string)", [ticker]).hex()
    data = call(OPEN_ORACLE, signature, payload, block)
    # price() returns 6 decimals
    return Decimal(int(data["result"][0 : 64 + 2], 16)) / E_6


def chainlink_ethUsdPrice(block="latest"):
    signature = CHAINLINK_ETH_USD_PRICE[:10]
    payload = ""
    data = call(CHAINLINK_ORACLE, signature, payload, block)
    # tokEthPrice() returns an ETH-USD price with 6 decimals
    return Decimal(int(data["result"][0 : 64 + 2], 16)) / E_6


def chainlink_tokEthPrice(ticker, block="latest"):
    signature = CHAINLINK_TOK_ETH_PRICE[:10]
    payload = encode_single("(string)", [ticker]).hex()
    data = call(CHAINLINK_ORACLE, signature, payload, block)
    # tokEthPrice() returns an ETH price with 8 decimals for some reason...
    return Decimal(int(data["result"][0 : 64 + 2], 16)) / E_8


def chainlink_tokUsdPrice(ticker, block="latest"):
    signature = CHAINLINK_TOK_USD_PRICE[:10]
    payload = encode_single("(string)", [ticker]).hex()
    data = call(CHAINLINK_ORACLE, signature, payload, block)
    # tokEthPrice() returns an ETH price with 8 decimals for some reason...
    return Decimal(int(data["result"][0 : 64 + 2], 16)) / E_8


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

def getPendingRewards(strategy, decimals, block="latest"):
    signature = "0xd9621f9e" # getPendingRewards()
    try:
        payload = ""
        data = call(strategy, signature, payload, block)
        return Decimal(int(data["result"][0 : 64 + 2], 16)) / Decimal(
            math.pow(10, decimals)
        )
    except Exception:
        log.error("getPendingRewards failed")
        return Decimal(0)


def strategyCheckBalance(strategy, coin_contract, decimals, block="latest"):
    signature = "0x5f515226"
    try:
        payload = encode_single("(address)", [coin_contract]).hex()
        data = call(strategy, signature, payload, block)
        if "error" in data:
            log.error(data["error"]["message"])
        return Decimal(int(data["result"][0 : 64 + 2], 16)) / Decimal(
            math.pow(10, decimals)
        )
    except Exception as e:
        log.error("strategyCheckBalance failed")
        log.error(f"strategy: {strategy}, coin_contract: {coin_contract}")
        log.error(e)
        return Decimal(0)


def rebasing_credits_per_token(block="latest", contract=OUSD):
    signature = "0x6691cb3d"  # rebasingCreditsPerToken()
    data = call(contract, signature, "", block)
    # this can happen if not live yet
    try:
        number = data["result"][0 : 64 + 2]
    except KeyError:
        return Decimal(0)
    if number == "0x":
        number = "0x0000000000000000000000000000000000000000000000000000000000000000"
    return Decimal(int(number, 16)) / E_18


def origin_token_rebasing_credits(block="latest", contract=OUSD):
    signature = "0x077f22b7"  # rebasingCredits()
    data = call(contract, signature, "", block)
    # this can happen if not live yet
    try:
        number = data["result"][0 : 64 + 2]
    except KeyError:
        return Decimal(0)
    if number == "0x":
        number = "0x0000000000000000000000000000000000000000000000000000000000000000"
    return Decimal(int(number, 16)) / E_18


def origin_token_non_rebasing_supply(block="latest", contract=OUSD):
    signature = "0xe696393a"  # nonRebasingSupply()
    data = call(contract, signature, "", block)
    # this can happen if not live yet
    try:
        number = data["result"][0 : 64 + 2]
    except KeyError:
        return Decimal(0)
    if number == "0x":
        number = "0x0000000000000000000000000000000000000000000000000000000000000000"
    return Decimal(int(number, 16)) / E_18


def ogn_staking_total_outstanding(block):
    data = storage_at(OGN_STAKING, 54, block)
    return Decimal(int(data["result"][0 : 64 + 2], 16)) / E_18


def story_staking_total_supply(block):
    signature = SIG_FUNC_TOTAL_SUPPLY[:10]
    data = call(STORY_STAKING_SERIES, signature, "", block)
    return Decimal(int(data["result"], 16)) / E_18


def story_staking_claiming_index(block):
    signature = SIG_FUNC_CURRENT_CLAIMING_INDEX[:10]
    data = call(STORY_STAKING_SERIES, signature, "", block)
    return int(data["result"], 16)


def story_staking_staking_index(block):
    signature = SIG_FUNC_CURRENT_STAKING_INDEX[:10]
    data = call(STORY_STAKING_SERIES, signature, "", block)
    return int(data["result"], 16)


def priceUSDMint(coin_contract, assetAddress, block="latest"):
    signature = SIG_FUNC_PRICE_USD_MINT[:10]  # priceUSDMint(address)
    payload = encode_single("(address)", [assetAddress]).hex()
    data = call(coin_contract, signature, payload, block)

    if data.get("error") is not None:
        raise RPCError(data["error"]["code"], data["error"]["message"])

    return Decimal(int(data["result"], 16)) / E_18


def priceUSDRedeem(coin_contract, assetAddress, block="latest"):
    signature = SIG_FUNC_PRICE_USD_REDEEM[:10]  # priceUSDRedeem(address)
    payload = encode_single("(address)", [assetAddress]).hex()
    data = call(coin_contract, signature, payload, block)

    if data.get("error") is not None:
        raise RPCError(data["error"]["code"], data["error"]["message"])

    return Decimal(int(data["result"], 16)) / E_18


def priceUnitMint(coin_contract, assetAddress, block="latest"):
    signature = SIG_FUNC_PRICE_UNIT_MINT[:10]  # priceUnitMint(address)
    payload = encode_single("(address)", [assetAddress]).hex()
    data = call(coin_contract, signature, payload, block)

    if data.get("error") is not None:
        raise RPCError(data["error"]["code"], data["error"]["message"])

    return Decimal(int(data["result"], 16)) / E_18


def priceUnitRedeem(coin_contract, assetAddress, block="latest"):
    signature = SIG_FUNC_PRICE_UNIT_REDEEM[:10]  # priceUnitRedeem(address)
    payload = encode_single("(address)", [assetAddress]).hex()
    data = call(coin_contract, signature, payload, block)

    if data.get("error") is not None:
        raise RPCError(data["error"]["code"], data["error"]["message"])

    return Decimal(int(data["result"], 16)) / E_18


def staking_durationRewardRate(address, duration, block="latest"):
    """ SingleAssetStaking.durationRewardRate(uint256 _duration) """
    signature = SIG_FUNC_DURATION_REWARD_RATE[:10]
    payload = encode_single("(uint256)", [duration]).hex()
    data = call(address, signature, payload, block)
    return Decimal(int(data["result"], 16))


def dripper_available(block="latest"):
    signature = SIG_DRIPPER_AVAILABLE_FUNDS[:10]
    data = call(DRIPPER, signature, "", block)
    return Decimal(int(data["result"], 16)) / E_6


def dripper_drip_rate(block="latest"):
    signature = SIG_DRIPPER_CONFIG[:10]
    data = call(DRIPPER, signature, "", block)
    return Decimal(int(data["result"][64 + 2 :], 16)) / E_6


class AaveLendingPoolCore:
    """ LendingPoolCore calls """

    @staticmethod
    def isReserveBorrowingEnabled(address, block="latest") -> bool:
        data = call_by_sig(
            AAVE_LENDING_POOL_CORE_V1,
            "isReserveBorrowingEnabled(address)",
            [address],
            block,
        )
        return data["result"] == TRUE_256BIT

    @staticmethod
    def getReserveAvailableLiquidity(
        address, decimals=18, block="latest"
    ) -> Decimal:
        return call_and_return_wad(
            AAVE_LENDING_POOL_CORE_V1,
            "getReserveAvailableLiquidity(address)",
            [address],
            block=block,
        )

    @staticmethod
    def getReserveTotalBorrowsStable(
        address, decimals=18, block="latest"
    ) -> Decimal:
        return call_and_return_wad(
            AAVE_LENDING_POOL_CORE_V1,
            "getReserveTotalBorrowsStable(address)",
            [address],
            block=block,
        )

    @staticmethod
    def getReserveTotalBorrowsVariable(address, block="latest") -> Decimal:
        return call_and_return_wad(
            AAVE_LENDING_POOL_CORE_V1,
            "getReserveTotalBorrowsVariable(address)",
            [address],
            block=block,
        )

    @staticmethod
    def getReserveTotalLiquidity(address, block="latest") -> Decimal:
        return call_and_return_wad(
            AAVE_LENDING_POOL_CORE_V1,
            "getReserveTotalLiquidity(address)",
            [address],
            block=block,
        )

    @staticmethod
    def getReserveCurrentLiquidityRate(address, block="latest") -> Decimal:
        # Return value is a "Ray" false decimal.  See: ds-math
        return call_and_return_ray(
            AAVE_LENDING_POOL_CORE_V1,
            "getReserveCurrentLiquidityRate(address)",
            [address],
            block=block,
        )

    @staticmethod
    def getReserveCurrentVariableBorrowRate(address, block="latest") -> Decimal:
        # Return value is a "Ray" false decimal.  See: ds-math
        return call_and_return_ray(
            AAVE_LENDING_POOL_CORE_V1,
            "getReserveCurrentVariableBorrowRate(address)",
            [address],
            block=block,
        )

    @staticmethod
    def getReserveCurrentStableBorrowRate(address, block="latest") -> Decimal:
        # Return value is a "Ray" false decimal.  See: ds-math
        return call_and_return_ray(
            AAVE_LENDING_POOL_CORE_V1,
            "getReserveCurrentStableBorrowRate(address)",
            [address],
            block=block,
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
            retval[symbol] = Decimal(ThreePool.balances(i)) / Decimal(
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

    @staticmethod
    def get_virtual_price(block="latest"):
        data = call_by_sig(CURVE_3POOL, "get_virtual_price()", [], block)
        result = data["result"]
        return decode_single("uint256", decode_hex(result))

    @staticmethod
    def get_balance_split(block="latest"):
        coins = ThreePool.get_all_coins(block)

        balances = {}
        pcts = {}
        total = Decimal(0)

        for i, coin in enumerate(coins):
            symbol = SYMBOL_FOR_CONTRACT[coin.lower()]
            decimals = DECIMALS_FOR_SYMBOL[symbol]
            bal = Decimal(ThreePool.balances(i))
            if decimals != 18:
                # Scale to 18 decimal places
                bal = bal * Decimal(math.pow(10, 18)) / Decimal(math.pow(10, decimals))
            balances[symbol] = bal
            total += bal

        for i, coin in enumerate(coins):
            symbol = SYMBOL_FOR_CONTRACT[coin.lower()]
            pcts[symbol] = balances.get(symbol, Decimal(0)) / total if total > 0 else 0

        return pcts

class ThreePoolStrat:
    """ RPC Calls for Convex Strategy """

    @staticmethod
    def assetToPToken(asset, block = "latest"):
        data = call_by_sig(STRATCONVEX1, "assetToPToken(address)", [asset], block)
        result = data["result"]
        return decode_single("address", decode_hex(result))

    @staticmethod
    def get_underlying_balance(block = "latest"):
        # Total number of tokens held in pool
        crv3_balance_split = ThreePool.get_balance_split(block)

        # LP token prices
        crv3_meta_vp = ThreePool.get_virtual_price(block)

        # Staked LP tokens
        staked_bal = balanceOf(CVX_3POOL_REWARDS_POOL, STRATCONVEX1, 18, block)
        
        # Unstaked LP tokens
        unstaked_bal = Decimal(0)
        for asset in (DAI, USDT, USDC):
            ptoken_addr = ThreePoolStrat.assetToPToken(asset, block)
            asset_unstaked_bal = balanceOf(ptoken_addr, STRATCONVEX1, 18, block)

            unstaked_bal += asset_unstaked_bal

        total_lp = staked_bal + unstaked_bal

        total_3crv_lp_value = total_lp * crv3_meta_vp
        
        retval = {}

        for asset in (DAI, USDT, USDC):
            symbol = SYMBOL_FOR_CONTRACT[asset.lower()]
            decimals = DECIMALS_FOR_SYMBOL[symbol]

            scaled_bal = total_3crv_lp_value * crv3_balance_split.get(symbol, 0)
            scaled_bal = scaled_bal / 10**18

            retval[symbol] = scaled_bal 
    
        return retval

class OUSDMetaPool:
    """ RPC Calls for OUSD<>3CRV MetaPool """

    @staticmethod
    def coins(index, block="latest"):
        data = call_by_sig(CURVE_METAPOOL, "coins(uint256)", [index], block=block)
        result = data["result"]
        return decode_single("address", decode_hex(result))

    @staticmethod
    def get_all_coins(block="latest"):
        return [
            OUSDMetaPool.coins(0), # OUSD
            OUSDMetaPool.coins(1), # 3CRV
        ]

    @staticmethod
    def get_all_balances(block="latest"):
        coins = OUSDMetaPool.get_all_coins(block)

        retval = {}

        for i, coin in enumerate(coins):
            symbol = SYMBOL_FOR_CONTRACT[coin.lower()]
            decimals = DECIMALS_FOR_SYMBOL[symbol]
            retval[symbol] = Decimal(OUSDMetaPool.balances(i)) / Decimal(
                math.pow(10, decimals)
            )

        return retval

    @staticmethod
    def balances(index, block="latest"):
        data = call_by_sig(CURVE_METAPOOL, "balances(uint256)", [index], block)
        result = data["result"]
        return decode_single("uint256", decode_hex(result))

    @staticmethod
    def get_virtual_price(block="latest"):
        data = call_by_sig(CURVE_METAPOOL, "get_virtual_price()", [], block)
        result = data["result"]
        return decode_single("uint256", decode_hex(result))

    @staticmethod
    def get_balance_split(block="latest"):
        coins = OUSDMetaPool.get_all_coins(block)

        balances = {}
        pcts = {}
        total = Decimal(0)

        for i, coin in enumerate(coins):
            symbol = SYMBOL_FOR_CONTRACT[coin.lower()]
            decimals = DECIMALS_FOR_SYMBOL[symbol]
            bal = Decimal(OUSDMetaPool.balances(i))
            if decimals != 18:
                # Scale to 18 decimal places
                bal = bal * Decimal(math.pow(10, 18)) / Decimal(math.pow(10, decimals))
            balances[symbol] = bal
            total += bal

        for i, coin in enumerate(coins):
            symbol = SYMBOL_FOR_CONTRACT[coin.lower()]
            pcts[symbol] = balances.get(symbol, Decimal(0)) / total if total > 0 else 0

        return pcts

class LUSDMetaPool:
    """ RPC Calls for LUSD<>3CRV MetaPool """

    @staticmethod
    def coins(index, block="latest"):
        data = call_by_sig(LUSD_METAPOOL, "coins(uint256)", [index], block=block)
        result = data["result"]
        return decode_single("address", decode_hex(result))

    @staticmethod
    def get_all_coins(block="latest"):
        return [
            LUSDMetaPool.coins(0), # LUSD
            LUSDMetaPool.coins(1), # 3CRV
        ]

    @staticmethod
    def get_all_balances(block="latest"):
        coins = LUSDMetaPool.get_all_coins(block)

        retval = {}

        for i, coin in enumerate(coins):
            symbol = SYMBOL_FOR_CONTRACT[coin.lower()]
            decimals = DECIMALS_FOR_SYMBOL[symbol]
            retval[symbol] = Decimal(LUSDMetaPool.balances(i)) / Decimal(
                math.pow(10, decimals)
            )

        return retval

    @staticmethod
    def balances(index, block="latest"):
        data = call_by_sig(LUSD_METAPOOL, "balances(uint256)", [index], block)
        result = data["result"]
        return decode_single("uint256", decode_hex(result))

    @staticmethod
    def get_virtual_price(block="latest"):
        data = call_by_sig(LUSD_METAPOOL, "get_virtual_price()", [], block)
        result = data["result"]
        return decode_single("uint256", decode_hex(result))

    @staticmethod
    def get_balance_split(block="latest"):
        coins = LUSDMetaPool.get_all_coins(block)

        balances = {}
        pcts = {}
        total = Decimal(0)

        for i, coin in enumerate(coins):
            symbol = SYMBOL_FOR_CONTRACT[coin.lower()]
            decimals = DECIMALS_FOR_SYMBOL[symbol]
            bal = Decimal(LUSDMetaPool.balances(i))
            if decimals != 18:
                # Scale to 18 decimal places
                bal = bal * Decimal(math.pow(10, 18)) / Decimal(math.pow(10, decimals))
            balances[symbol] = bal
            total += bal

        for i, coin in enumerate(coins):
            symbol = SYMBOL_FOR_CONTRACT[coin.lower()]
            pcts[symbol] = balances.get(symbol, Decimal(0)) / total if total > 0 else 0

        return pcts

class OUSDMetaStrategy:
    """ RPC Calls for OUSD MetaStrategy """

    @staticmethod
    def assetToPToken(asset, block = "latest"):
        data = call_by_sig(OUSD_METASTRAT, "assetToPToken(address)", [asset], block)
        result = data["result"]
        return decode_single("address", decode_hex(result))

    @staticmethod
    def get_underlying_balance(block = "latest"):
        # Total number of tokens held in pool
        ousd_balance_split = OUSDMetaPool.get_balance_split(block)
        crv3_balance_split = ThreePool.get_balance_split(block)

        # LP token price
        ousd_meta_vp = OUSDMetaPool.get_virtual_price(block)

        # Staked LP tokens
        staked_bal = balanceOf(CVX_OUSD_REWARDS_POOL, OUSD_METASTRAT, 18, block)
        
        # Unstaked LP tokens
        unstaked_bal = Decimal(0)
        for asset in (DAI, USDT, USDC):
            ptoken_addr = OUSDMetaStrategy.assetToPToken(asset, block)
            asset_unstaked_bal = balanceOf(ptoken_addr, OUSD_METASTRAT, 18, block)

            unstaked_bal += asset_unstaked_bal

        total_lp = (staked_bal + unstaked_bal) * ousd_meta_vp / 10**18

        total_ousd_lp_value = total_lp * ousd_balance_split.get("OUSD", 0)
        total_3crv_lp_value = total_lp * ousd_balance_split.get("3CRV", 0)
        
        retval = {
            'OUSD': total_ousd_lp_value
        }

        for asset in (DAI, USDT, USDC):
            symbol = SYMBOL_FOR_CONTRACT[asset.lower()]
            decimals = DECIMALS_FOR_SYMBOL[symbol]

            scaled_bal = total_3crv_lp_value * crv3_balance_split.get(symbol, 0)

            retval[symbol] = scaled_bal
    
        return retval

class LUSDMetaStrategy:
    """ RPC Calls for LUSD MetaStrategy """

    @staticmethod
    def assetToPToken(asset, block = "latest"):
        data = call_by_sig(LUSD_METASTRAT, "assetToPToken(address)", [asset], block)
        result = data["result"]
        return decode_single("address", decode_hex(result))

    @staticmethod
    def get_underlying_balance(block = "latest"):
        # Total number of tokens held in pool
        lusd_balance_split = LUSDMetaPool.get_balance_split(block)
        crv3_balance_split = ThreePool.get_balance_split(block)

        # LP token price
        lusd_meta_vp = LUSDMetaPool.get_virtual_price(block)

        # Staked LP tokens
        staked_bal = balanceOf(CVX_LUSD_REWARDS_POOL, LUSD_METASTRAT, 18, block)
        
        # Unstaked LP tokens
        unstaked_bal = Decimal(0)
        for asset in (DAI, USDT, USDC):
            ptoken_addr = LUSDMetaStrategy.assetToPToken(asset, block)
            asset_unstaked_bal = balanceOf(ptoken_addr, LUSD_METASTRAT, 18, block)

            unstaked_bal += asset_unstaked_bal

        total_lp = (staked_bal + unstaked_bal) * lusd_meta_vp / 10**18

        total_lusd_lp_value = total_lp * lusd_balance_split.get("LUSD", 0)
        total_3crv_lp_value = total_lp * lusd_balance_split.get("3CRV", 0)
        
        retval = {
            'LUSD': total_lusd_lp_value
        }

        for asset in (DAI, USDT, USDC):
            symbol = SYMBOL_FOR_CONTRACT[asset.lower()]
            decimals = DECIMALS_FOR_SYMBOL[symbol]

            scaled_bal = total_3crv_lp_value * crv3_balance_split.get(symbol, 0)

            retval[symbol] = scaled_bal
    
        return retval

class GenericCurveAMOStrategy:
    def __init__(self, strategy_addr, metapool_addr, rewards_pool_addr, all_coins):
        self.strategy_addr = strategy_addr
        self.metapool_addr = metapool_addr
        self.rewards_pool_addr = rewards_pool_addr
        self.all_coins = all_coins
    
    """ RPC Calls for LUSD<>3CRV MetaPool """

    def coins(self, index, block="latest"):
        data = call_by_sig(self.metapool_addr, "coins(uint256)", [index], block=block)
        result = data["result"]
        return decode_single("address", decode_hex(result))

    def get_all_coins(self, block="latest"):
        return [self.coins(x) for x in range(0, len(self.all_coins))]

    def get_all_balances(self, block="latest"):
        coins = self.get_all_coins(block)

        retval = {}

        for i, coin in enumerate(coins):
            symbol = SYMBOL_FOR_CONTRACT[coin.lower()]
            decimals = DECIMALS_FOR_SYMBOL[symbol]
            retval[symbol] = Decimal(self.balances(i)) / Decimal(
                math.pow(10, decimals)
            )

        return retval

    def balances(self, index, block="latest"):
        data = call_by_sig(self.metapool_addr, "balances(uint256)", [index], block)
        result = data["result"]
        return decode_single("uint256", decode_hex(result))

    def get_virtual_price(self, block="latest"):
        data = call_by_sig(self.metapool_addr, "get_virtual_price()", [], block)
        result = data["result"]
        return decode_single("uint256", decode_hex(result))

    def get_balance_split(self, block="latest"):
        coins = self.get_all_coins(block)

        balances = {}
        pcts = {}
        total = Decimal(0)

        for i, coin in enumerate(coins):
            symbol = SYMBOL_FOR_CONTRACT[coin.lower()]
            decimals = DECIMALS_FOR_SYMBOL[symbol]
            bal = Decimal(self.balances(i))
            if decimals != 18:
                # Scale to 18 decimal places
                bal = bal * Decimal(math.pow(10, 18)) / Decimal(math.pow(10, decimals))
            balances[symbol] = bal
            total += bal

        for i, coin in enumerate(coins):
            symbol = SYMBOL_FOR_CONTRACT[coin.lower()]
            pcts[symbol] = balances.get(symbol, Decimal(0)) / total if total > 0 else 0

        return pcts

    def asset_to_ptoken(self, asset, block = "latest"):
        data = call_by_sig(self.strategy_addr, "assetToPToken(address)", [asset], block)
        result = data["result"]
        return decode_single("address", decode_hex(result))

    def get_underlying_balance(self, block = "latest"):
        retval = {}

        # Total number of tokens held in pool
        coins_split = self.get_balance_split(block)

        # LP token price
        lp_price = self.get_virtual_price(block)

        # Staked LP tokens
        staked_bal = balanceOf(self.rewards_pool_addr, self.strategy_addr, 18, block)

        # Unstaked LP tokens
        unstaked_bal = Decimal(0)
        for asset_symbol in self.all_coins:
            if asset_symbol == "OETH":
                continue
            asset = CONTRACT_FOR_SYMBOL[asset_symbol]
            ptoken_addr = self.asset_to_ptoken(asset, block)
            asset_unstaked_bal = balanceOf(ptoken_addr, self.strategy_addr, 18, block)

            unstaked_bal += asset_unstaked_bal

        # Total LP tokens
        total_lp = (staked_bal + unstaked_bal) * lp_price / 10**18

        for asset_symbol in self.all_coins:
            retval[asset_symbol] = coins_split.get(asset_symbol, Decimal(0)) * total_lp

        return retval


OETHCurveAMOStrategy = GenericCurveAMOStrategy(
    OETH_CURVE_AMO_STRATEGY,
    OETH_ETH_AMO_METAPOOL,
    OETH_CURVE_AMO_REWARDS_POOL,
    ("ETH", "OETH")
)
