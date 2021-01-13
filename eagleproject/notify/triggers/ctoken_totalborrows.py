from decimal import Decimal
from statistics import mean
from core.addresses import CONTRACT_ADDR_TO_NAME
from core.common import dict_append
from notify.events import event_critical, event_high

PERCENT_DIFF_THRESHOLD = Decimal(0.05)


def get_past_comparison(ctoken_snaps):
    """ Get the historical comparison value.  It will either be an average of
    past values, last value, or 0, depending on what is available. """

    count = len(ctoken_snaps)

    if count < 2:
        return 0

    elif count > 2:
        return mean([x.total_borrows for x in ctoken_snaps[1:]])

    return ctoken_snaps[1].total_borrows


def run_trigger(recent_ctoken_snapshots):
    """ Trigger on extreme supply changes in cTokens """
    events = []
    snaps = {}

    for snap in recent_ctoken_snapshots:
        dict_append(snaps, snap.address, snap)

    for ctoken_address in snaps:
        total_borrows_comp = get_past_comparison(snaps[ctoken_address])
        total_borrows_current = snaps[ctoken_address][0].total_borrows
        diff_threshold = total_borrows_comp * PERCENT_DIFF_THRESHOLD

        if total_borrows_current < total_borrows_comp:
            diff = total_borrows_comp - total_borrows_current

            if diff > diff_threshold:
                events.append(event_critical(
                    "Compound cToken Total Borrows Fluctuation   🚨",
                    "The cToken {} borrows have dropped more than {}% between "
                    "snapshots.".format(
                        CONTRACT_ADDR_TO_NAME.get(
                            ctoken_address,
                            ctoken_address
                        ),
                        round(PERCENT_DIFF_THRESHOLD * Decimal(100))
                    )
                ))

        else:
            diff = total_borrows_current - total_borrows_comp

            if diff > diff_threshold:
                events.append(event_high(
                    "Compound cToken Total Borrows Fluctuation   🚨",
                    "The cToken {} has gained more than {}% borrows between "
                    "snapshots.".format(
                        CONTRACT_ADDR_TO_NAME.get(
                            ctoken_address,
                            ctoken_address
                        ),
                        round(PERCENT_DIFF_THRESHOLD * Decimal(100))
                    )
                ))

    return events
