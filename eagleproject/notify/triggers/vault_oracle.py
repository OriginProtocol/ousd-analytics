""" Oracle prices drift """
import locale
from decimal import Decimal
from core.blockchain.addresses import OUSD_VAULT
from core.blockchain.const import CONTRACT_FOR_SYMBOL
from core.blockchain.rpc import RPCError, priceUSDMint, priceUSDRedeem
from notify.events import event_high

# USD-pegged stable coins drift thresholds
MAX_USD_PRICE = Decimal("1.05")
MIN_USD_PRICE = Decimal("0.95")
ONE_E8 = Decimal(1e8)

# TODO: Necessary?
locale.setlocale(locale.LC_ALL, "en_US.UTF-8")


def get_oracle_prices(symbol):
    """ Get min/max price for a token """
    address = CONTRACT_FOR_SYMBOL[symbol]
    return (priceUSDRedeem(OUSD_VAULT, address), priceUSDMint(OUSD_VAULT, address))


def assert_price_in_bounds(symbol):
    max_price, min_price = get_oracle_prices(symbol)

    assert (
        max_price <= MAX_USD_PRICE
    ), "{} price exceeds upper bound ({})".format(
        symbol,
        locale.currency(max_price),
    )

    assert (
        min_price >= MIN_USD_PRICE
    ), "{} price lower than acceptable lower bound ({})".format(
        symbol,
        locale.currency(min_price),
    )


def run_trigger(transfers, new_transfers):
    """ Template trigger """
    events = []

    for symbol in ["DAI", "USDT", "USDC"]:
        try:
            assert_price_in_bounds(symbol)
        except AssertionError as e:
            events.append(
                event_high("Exceptional Oracle Price    🧙‍♀️", str(e))
            )
        except RPCError as e:
            events.append(event_high("Oracle Price Revert    🔴", str(e)))

    return events
