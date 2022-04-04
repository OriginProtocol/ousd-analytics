from django.conf import settings
from core.common import format_ogn_human
from notify.events import event_critical, event_high, event_normal, event_low

LOW_YELLOW = 25000
LOW_ORANGE = 10000
LOW_RED = 500
EVENT_TAGS = ['ogn']


def run_trigger(ogn_staking_snapshot):
    """ Trigger to alert when the buffer of OGN to cover new staking rewards is
    low """
    events = []

    # If no snapshot has been made yet, ignore
    if ogn_staking_snapshot is None:
        return events

    block_number = ogn_staking_snapshot.block_number
    balance = ogn_staking_snapshot.ogn_balance
    outstanding = ogn_staking_snapshot.total_outstanding
    diff = balance - outstanding

    if diff < 1:
        # Should be impossible due to contract protections
        events.append(
            event_critical(
                "Impossible staking condition   ⁉️",
                "OGN Staking has less OGN than expected rewards "
                "({} OGN)".format(diff),
                tags=EVENT_TAGS,
                block_number=block_number
            )
        )
    elif diff < LOW_RED:
        # 🤏
        events.append(
            event_critical(
                "Critical OGN Staking contract buffer   🟥",
                "OGN Staking contract rewards buffer down to {}".format(
                    format_ogn_human(diff)
                ),
                tags=EVENT_TAGS,
                block_number=block_number
            )
        )
    elif diff < LOW_ORANGE:
        events.append(
            event_high(
                "Low OGN Staking contract buffer   🟧",
                "OGN Staking contract rewards buffer down to {}".format(
                    format_ogn_human(diff)
                ),
                tags=EVENT_TAGS,
                block_number=block_number
            )
        )
    elif diff < LOW_YELLOW:
        events.append(
            event_normal(
                "OGN Staking contract buffer   🟨",
                "OGN Staking contract rewards buffer down to {}".format(
                    format_ogn_human(diff)
                ),
                tags=EVENT_TAGS,
                block_number=block_number
            )
        )
    # Debug only
    elif settings.DEBUG:
        events.append(
            event_low(
                "Nominal OGN Staking contract buffer   🟩",
                "OGN Staking contract rewards buffer down to {}".format(
                    format_ogn_human(diff)
                ),
                tags=EVENT_TAGS,
                block_number=block_number
            )
        )

    return events
