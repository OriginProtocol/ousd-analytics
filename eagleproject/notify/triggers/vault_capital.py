from django.db.models import Q
from core.blockchain.sigs import (
    SIG_EVENT_CAPITAL_PAUSED,
    SIG_EVENT_CAPITAL_UNPAUSED,
)
from notify.events import event_high


def get_pause_events(logs):
    """ Get DepositsPaused/DepositsUnpaused events """
    return logs.filter(
        Q(topic_0=SIG_EVENT_CAPITAL_PAUSED)
        | Q(topic_0=SIG_EVENT_CAPITAL_UNPAUSED)
    ).order_by('block_number')


def run_trigger(new_logs):
    """ Template trigger """
    events = []

    for ev in get_pause_events(new_logs):
        is_pause = ev.topic_0 == SIG_EVENT_CAPITAL_PAUSED

        events.append(
            event_high(
                "Capital Paused   ⏸️" if is_pause else "Capital Unpaused   ▶️",
                "OUSD Vault capital has been {}".format(
                    "paused" if is_pause else "unpaused",
                )
            )
        )

    return events
