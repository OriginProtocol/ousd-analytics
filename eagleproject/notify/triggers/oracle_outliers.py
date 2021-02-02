from numpy import percentile
from datetime import datetime, timedelta

from core.models import OracleSnapshot
from core.blockchain.addresses import MIX_ORACLE, CHAINLINK_ORACLE, OPEN_ORACLE
from core.common import format_decimal
from notify.events import event_normal

# Blocks per week
WEEK = 60 * 60 * 24 * 7 / 15
PERCENTILE_HIGH = 95
PERCENTILE_LOW = 5
CACHE_DURATION_MINUTES = 60
ORACLE_TO_NAME = {
    MIX_ORACLE: "MixOracle",
    CHAINLINK_ORACLE: "ChainlinkOracle",
    OPEN_ORACLE: "Open Price Oracle",
}

CACHE = {}


def get_past_week(latest_block):
    """ Get details on the past week """
    global CACHE

    if (
        CACHE.get("past_week")
        and CACHE["past_week"].get("expiry") > datetime.now()
    ):
        return CACHE["past_week"]

    snaps = OracleSnapshot.objects.filter(block_number__gt=latest_block - WEEK)
    eth_usd_snaps = snaps.filter(ticker_left="ETH", ticker_right="USD")
    dai_eth_snaps = snaps.filter(ticker_left="DAI", ticker_right="ETH")
    usdc_eth_snaps = snaps.filter(ticker_left="USDC", ticker_right="ETH")
    usdt_eth_snaps = snaps.filter(ticker_left="USDT", ticker_right="ETH")
    dai_usd_snaps = snaps.filter(ticker_left="DAI", ticker_right="USD")
    usdc_usd_snaps = snaps.filter(ticker_left="USDC", ticker_right="USD")
    usdt_usd_snaps = snaps.filter(ticker_left="USDT", ticker_right="USD")

    CACHE["past_week"] = {
        "expiry": datetime.now() + timedelta(minutes=CACHE_DURATION_MINUTES),
        "result": {
            "ETH-USD": [x.price for x in eth_usd_snaps],
            "DAI-ETH": [x.price for x in dai_eth_snaps],
            "USDC-ETH": [x.price for x in usdc_eth_snaps],
            "USDT-ETH": [x.price for x in usdt_eth_snaps],
            "DAI-USD": [x.price for x in dai_usd_snaps],
            "USDC-USD": [x.price for x in usdc_usd_snaps],
            "USDT-USD": [x.price for x in usdt_usd_snaps],
        },
    }

    return CACHE["past_week"]


def get_outlier_prices(latest_block, new_snapshotss,
                       high_percentile=PERCENTILE_HIGH,
                       low_percentile=PERCENTILE_LOW):
    """ Find the outlier prices outside of the expected from the new set of
    snapshots compared to all from the last week
    """
    outliers = []  # List of snapshots
    past_week = get_past_week(latest_block)

    for snap in new_snapshotss:
        # IDK statistics magic
        q1, q3 = percentile(
            sorted(map(
                float,
                past_week["result"]["{}-{}".format(
                    snap.ticker_left,
                    snap.ticker_right
                )]
            )),
            (low_percentile, high_percentile)
        )

        # Interquartile range
        iqr = q3 - q1

        # find lower and upper bounds, lower shouldn't be less than 0
        upper_bound = q3 + (1.5 * iqr)
        lower_bound = q1 - (1.5 * iqr)
        if lower_bound < 0:
            lower_bound = 0

        # In the edge case where there has been no deviation in price yet (e.g.
        # price has always been 1), there's nothing extraordinary yet
        if upper_bound == lower_bound:
            continue

        # Find any outliers from the latest group of snapshots
        if snap.price <= lower_bound or snap.price >= upper_bound:
            outliers.append(snap)

    return outliers


def run_trigger(snapshot_cursor, latest_snapshot_block, oracle_snapshots):
    """ Trigger when oracle prices deviate too far """

    # Don't repeat alerts for the same snapshot
    if snapshot_cursor.block_number == latest_snapshot_block:
        return []

    events = []
    outliers = get_outlier_prices(latest_snapshot_block, oracle_snapshots)

    if outliers:
        for snap in outliers:
            price = format_decimal(snap.price)

            events.append(
                event_normal(
                    "{} price deviation   🧙‍♀️".format(
                        ORACLE_TO_NAME[snap.oracle]
                    ),
                    "{} @ {} {}\n\n".format(
                        snap.ticker_left,
                        price,
                        snap.ticker_right,
                    ),
                    block_number=snap.block_number
                )
            )

    return events
