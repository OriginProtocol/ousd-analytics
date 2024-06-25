""" Oracle prices drift """
import locale
from decimal import Decimal
from core.blockchain.addresses import OUSD_VAULT, OETH_VAULT
from core.blockchain.const import CONTRACT_FOR_SYMBOL
from core.blockchain.rpc import RPCError, priceUSDMint, priceUSDRedeem, priceUnitMint, priceUnitRedeem
from notify.events import event_high

from core.blockchain.strategies import OUSD_BACKING_ASSETS, OETH_BACKING_ASSETS

from time import sleep
from datetime import timedelta

DEDUPE_WINDOW_SECONDS = timedelta(days=1)  # 1d

# USD-pegged stable coins drift thresholds
MAX_USD_PRICE = Decimal("1.05")
MIN_USD_PRICE = Decimal("0.95")

MAX_ETH_PRICE = Decimal("1.03")
MIN_ETH_PRICE = Decimal("0.97")

ONE_E8 = Decimal(1e8)

# TODO: Necessary?
locale.setlocale(locale.LC_ALL, "en_US.UTF-8")

def get_oracle_prices(symbol, vault=OUSD_VAULT):
    """ Get min/max price for a token """
    address = CONTRACT_FOR_SYMBOL[symbol]
    return (priceUnitRedeem(vault, address), priceUnitMint(vault, address))


def assert_price_in_bounds(symbol):
    is_ousd = symbol in OUSD_BACKING_ASSETS
    max_price, min_price = get_oracle_prices(symbol, OUSD_VAULT if is_ousd else OETH_VAULT)

    if symbol != "RETH":
        # RETH accrues value rather than rebasing to increase supply
        assert (
            max_price <= MAX_USD_PRICE if is_ousd else max_price <= MAX_ETH_PRICE
        ), "{} price exceeds upper bound ({})".format(
            symbol,
            locale.currency(max_price),
        )

    assert (
        min_price >= MIN_USD_PRICE if is_ousd else min_price >= MIN_ETH_PRICE
    ), "{} price lower than acceptable lower bound ({})".format(
        symbol,
        locale.currency(min_price),
    )


def run_trigger():
    """ Template trigger """
    events = []

    for assets in [OUSD_BACKING_ASSETS, OETH_BACKING_ASSETS]:
        for symbol in assets:
            if symbol == "FRXETH":
                continue
            retries = 3
            while retries > 0:
                retries = retries - 1
                try:
                    assert_price_in_bounds(symbol)
                    continue
                except AssertionError as e:
                    events.append(
                        event_high(
                            "Exceptional Oracle Price    🧙‍♀️", 
                            str(e),
                            deduplicate_time_window=DEDUPE_WINDOW_SECONDS,
                        )
                    )
                    continue
                except RPCError as e:
                    print("RPC Error when reading price for {}".format(symbol), e)
                    if "Asset price" in e.message or retries <= 0:
                        events.append(
                            event_high(
                                "RPC Error when reading price for {}    🔴".format(symbol), 
                                str(e),
                                deduplicate_time_window=DEDUPE_WINDOW_SECONDS,
                            ),
                        )
                        break
                    elif retries > 0:
                        sleep(3)

    return events
