from numpy import percentile
from datetime import datetime, timedelta
from statistics import median
from core.common import format_ousd_human
from notify.events import event_low

CACHE_DURATION_MINUTES = 30

CACHE = {}


def get_past_week(transfers):
    """ Get details on the past week """
    global CACHE

    if (
        CACHE.get("past_week")
        and CACHE["past_week"].get("expiry") > datetime.now()
    ):
        return CACHE["past_week"]

    one_week_ago = datetime.now() - timedelta(days=7)
    transfers = transfers.filter(block_time__gt=one_week_ago)
    values = [t.amount for t in transfers]

    CACHE["past_week"] = {
        "expiry": datetime.now() + timedelta(minutes=CACHE_DURATION_MINUTES),
        "result": {
            "min_value": min(values),
            "max_value": max(values),
            "median_value": median(values),
            "values": values,
            "transfers": transfers,
        },
    }

    return CACHE["past_week"]


def get_outlier_transfers(transfers, new_transfers, high_percentile=95,
                          low_percentile=5):
    """ Find the outlier transfers with values outside of the expected from the
    new set of transfers compared to all from the last week
    """
    outliers = []
    past_week = get_past_week(transfers)

    # IDK statistics magic
    q1, q3 = percentile(
        sorted(map(float, past_week["result"]["values"])),
        (low_percentile, high_percentile)
    )

    # Interquartile range
    iqr = q3 - q1

    # find lower and upper bounds, lower shouldn't be less than 0
    upper_bound = q3 + (1.5 * iqr)
    lower_bound = q1 - (1.5 * iqr)
    if lower_bound < 0:
        lower_bound = 0

    # Find any outliers from the latest group of transactions
    for t in new_transfers:
        if t.amount <= lower_bound or t.amount >= upper_bound:
            outliers.append(t)

    return outliers


def run_trigger(transfers, new_transfers):
    """ Check OUSD transactions for general unusuality """
    events = []

    """ Look for outlier transfers that could warrant an eyeball """
    unusual_transfers = get_outlier_transfers(transfers, new_transfers)

    if unusual_transfers:
        for transfer in unusual_transfers:
            events.append(
                event_low(
                    "Exceptional transfer   👽",
                    "{} transferred {} OUSD\n\n"
                    "Transaction: https://etherscan.io/tx/{}".format(
                        transfer.from_address,
                        format_ousd_human(transfer.amount),
                        transfer.tx_hash_id,
                    )
                )
            )

    return events
