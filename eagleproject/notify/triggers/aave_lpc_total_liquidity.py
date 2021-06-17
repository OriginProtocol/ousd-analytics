from decimal import Decimal
from statistics import mean
from core.blockchain.addresses import CONTRACT_ADDR_TO_NAME
from core.common import dict_append
from notify.events import event_critical, event_high, event_normal

PERCENT_DIFF_THRESHOLD_NOTICE = Decimal(0.05)
PERCENT_DIFF_THRESHOLD_WARNING = Decimal(0.10)
PERCENT_DIFF_THRESHOLD_CRITICAL = Decimal(0.15)


def get_past_comparison(reserve_snaps):
    """ Get the historical comparison value.  It will either be an average of
    past values, last value, or 0, depending on what is available. """

    count = len(reserve_snaps)

    if count < 2:
        return 0

    elif count > 2:
        return mean([x.total_liquidity for x in reserve_snaps[1:]])

    return reserve_snaps[1].total_liquidity


def run_trigger(recent_aave_reserve_snapshots):
    """ Trigger on extreme supply changes in Aave LPC reserves """
    events = []
    snaps = {}

    for snap in recent_aave_reserve_snapshots:
        dict_append(snaps, snap.asset, snap)

    for asset in snaps:
        total_liquidity_comp = get_past_comparison(snaps[asset])
        total_liquidity_current = snaps[asset][0].total_liquidity
        notice_diff_threshold = (
            total_liquidity_comp * PERCENT_DIFF_THRESHOLD_NOTICE
        )
        warning_diff_threshold = (
            total_liquidity_comp * PERCENT_DIFF_THRESHOLD_WARNING
        )
        critical_diff_threshold = (
            total_liquidity_comp * PERCENT_DIFF_THRESHOLD_CRITICAL
        )

        ev_func = event_normal
        title = ""
        msg = ""
        threshold = 0

        if total_liquidity_current < total_liquidity_comp:
            diff = total_liquidity_comp - total_liquidity_current

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
                title = "Aave Liquidity Fluctuation   🚨"
                msg = (
                    "The LendingPoolCore {} reserve has dropped more than {}% "
                    "between snapshots.".format(
                        CONTRACT_ADDR_TO_NAME.get(asset, asset),
                        round(threshold * Decimal(100))
                    )
                )

        else:
            diff = total_liquidity_current - total_liquidity_comp

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
                title = "Aave Liquidity Fluctuation   🚨"
                msg = (
                    "The LendingPoolCore {} reserve has gained more than {}% "
                    "between snapshots.".format(
                        CONTRACT_ADDR_TO_NAME.get(asset, asset),
                        round(threshold * Decimal(100))
                    )
                )

        if threshold:
            events.append(
                ev_func(title, msg, block_number=snaps[asset][0].block_number)
            )

    return events
