""" Oracle prices drift """
import locale
from decimal import Decimal
from core.blockchain.addresses import OUSD_VAULT
from core.blockchain.const import CONTRACT_FOR_SYMBOL
from core.blockchain.rpc import RPCError, priceUSDMint, priceUSDRedeem, priceUnitMint, priceUnitRedeem
from notify.events import event_high

from core.blockchain.strategies import OUSD_BACKING_ASSETS, OETH_BACKING_ASSETS

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

    if vault == OUSD_VAULT:
        # Rel: https://github.com/OriginProtocol/origin-dollar/issues/1368
        return (priceUSDRedeem(vault, address), priceUSDMint(vault, address))

    return (priceUnitRedeem(vault, address), priceUnitMint(vault, address))


def assert_price_in_bounds(symbol):
    max_price, min_price = get_oracle_prices(symbol)

    if symbol != "RETH":
        # RETH accrues value rather than rebasing to increase supply
        assert (
            max_price <= MAX_USD_PRICE if symbol in OUSD_BACKING_ASSETS else max_price <= MAX_ETH_PRICE
        ), "{} price exceeds upper bound ({})".format(
            symbol,
            locale.currency(max_price),
        )

    assert (
        min_price >= MIN_USD_PRICE if symbol in OUSD_BACKING_ASSETS else min_price >= MIN_ETH_PRICE
    ), "{} price lower than acceptable lower bound ({})".format(
        symbol,
        locale.currency(min_price),
    )


def run_trigger(transfers, new_transfers):
    """ Template trigger """
    events = []

    for assets in [OUSD_BACKING_ASSETS, OETH_BACKING_ASSETS]:
        for symbol in assets:
            try:
                assert_price_in_bounds(symbol)
            except AssertionError as e:
                events.append(
                    event_high("Exceptional Oracle Price    🧙‍♀️", str(e))
                )
            except RPCError as e:
                events.append(event_high("Oracle Price Revert for {}    🔴".format(symbol), str(e)))

    return events
