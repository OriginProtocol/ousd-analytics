from decimal import Decimal
from statistics import mean
from core.blockchain.addresses import CONTRACT_ADDR_TO_NAME
from core.common import dict_append
from notify.events import event_critical, event_high, event_normal

PERCENT_DIFF_THRESHOLD_NOTICE = Decimal(0.05)
PERCENT_DIFF_THRESHOLD_WARNING = Decimal(0.10)
PERCENT_DIFF_THRESHOLD_CRITICAL = Decimal(0.15)


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
    ev_func = event_normal

    for snap in recent_ctoken_snapshots:
        dict_append(snaps, snap.address, snap)

    for ctoken_address in snaps:
        total_borrows_comp = get_past_comparison(snaps[ctoken_address])
        total_borrows_current = snaps[ctoken_address][0].total_borrows
        notice_diff_threshold = (
            total_borrows_comp * PERCENT_DIFF_THRESHOLD_NOTICE
        )
        warning_diff_threshold = (
            total_borrows_comp * PERCENT_DIFF_THRESHOLD_WARNING
        )
        critical_diff_threshold = (
            total_borrows_comp * PERCENT_DIFF_THRESHOLD_CRITICAL
        )

        title = ""
        msg = ""
        threshold = 0

        if total_borrows_current < total_borrows_comp:
            diff = total_borrows_comp - total_borrows_current

            if diff > critical_diff_threshold:
                ev_func = event_critical
                threshold = PERCENT_DIFF_THRESHOLD_CRITICAL

            elif diff > warning_diff_threshold:
                ev_func = event_high
                threshold = PERCENT_DIFF_THRESHOLD_WARNING

            elif diff > notice_diff_threshold:
                ev_func = event_normal
                threshold = PERCENT_DIFF_THRESHOLD_NOTICE

            if threshold:
                title = "Compound cToken Total Borrows Fluctuation   🚨"
                msg = (
                    "The cToken {} borrows have dropped more than {}% between "
                    "snapshots.".format(
                        CONTRACT_ADDR_TO_NAME.get(
                            ctoken_address,
                            ctoken_address
                        ),
                        round(threshold * Decimal(100))
                    )
                )

        else:
            diff = total_borrows_current - total_borrows_comp

            if diff > critical_diff_threshold:
                ev_func = event_critical
                threshold = PERCENT_DIFF_THRESHOLD_CRITICAL

            elif diff > warning_diff_threshold:
                ev_func = event_high
                threshold = PERCENT_DIFF_THRESHOLD_WARNING

            elif diff > notice_diff_threshold:
                ev_func = event_normal
                threshold = PERCENT_DIFF_THRESHOLD_NOTICE

            if threshold:
                title = "Compound cToken Total Borrows Fluctuation   🚨"
                msg = (
                    "The cToken {} has gained more than {}% borrows between "
                    "snapshots.".format(
                        CONTRACT_ADDR_TO_NAME.get(
                            ctoken_address,
                            ctoken_address
                        ),
                        round(threshold * Decimal(100))
                    )
                )

        if threshold:
            events.append(ev_func(title, msg))

    return events
