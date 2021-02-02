from decimal import Decimal
from statistics import mean
from core.blockchain.addresses import CONTRACT_ADDR_TO_NAME
from core.blockchain.const import (
    CTOKEN_DECIMALS,
    DECIMALS_FOR_SYMBOL,
    SYMBOL_FOR_COMPOUND,
)
from core.blockchain.conversion import ctoken_to_underlying
from core.common import Direction, dict_append, format_decimal
from notify.events import event_critical, event_high, event_normal

PERCENT_DIFF_THRESHOLD_NOTICE = Decimal(0.05)
PERCENT_DIFF_THRESHOLD_WARNING = Decimal(0.10)
PERCENT_DIFF_THRESHOLD_CRITICAL = Decimal(0.15)


def create_message(action, ctoken_name, diff, diff_underlying, symbol,
                   pct_threshold, emoji):
    dir_symbol = "+" if action == Direction.GAIN else "-"
    dir_desc = "gained" if action == Direction.GAIN else "lost"
    title = "Compound cToken Total Borrows Fluctuation   {}".format(emoji)
    msg = (
        "The cToken {} borrows have {} more than ({}%) between snapshots.\n\n"
        "c{}: {}{}\n"
        "{} (approx): {}{}".format(
            ctoken_name,
            dir_desc,
            round(pct_threshold * Decimal(100)),
            symbol,
            dir_symbol,
            format_decimal(diff, max_decimals=CTOKEN_DECIMALS),
            symbol,
            dir_symbol,
            format_decimal(
                diff_underlying,
                max_decimals=DECIMALS_FOR_SYMBOL.get(symbol, 4)
            ),
        )
    )

    return title, msg


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
        underlying_symbol = SYMBOL_FOR_COMPOUND.get(ctoken_address, '')

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

            underlying_diff = ctoken_to_underlying(
                underlying_symbol,
                diff,
                snap.block_number
            )

            if threshold:
                title, msg = create_message(
                    Direction.LOSS,
                    CONTRACT_ADDR_TO_NAME.get(
                        ctoken_address,
                        ctoken_address
                    ),
                    diff,
                    underlying_diff,
                    underlying_symbol,
                    threshold,
                    "🚨",
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

            underlying_diff = ctoken_to_underlying(
                underlying_symbol,
                diff,
                snap.block_number
            )

            if threshold:
                title, msg = create_message(
                    Direction.GAIN,
                    CONTRACT_ADDR_TO_NAME.get(
                        ctoken_address,
                        ctoken_address
                    ),
                    diff,
                    underlying_diff,
                    underlying_symbol,
                    threshold,
                    "🚨",
                )

        if threshold:
            events.append(ev_func(
                title,
                msg,
                block_number=snaps[ctoken_address][0].block_number
            ))

    return events
