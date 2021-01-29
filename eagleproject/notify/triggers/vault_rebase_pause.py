""" RebasePaused/RebaseUnpaused events """
from django.db.models import Q
from core.blockchain.sigs import (
    SIG_EVENT_REBASE_PAUSED,
    SIG_EVENT_REBASE_UNPAUSED,
)
from notify.events import event_high


def get_pause_events(logs):
    """ Get DepositsPaused/DepositsUnpaused events """
    return logs.filter(
        Q(topic_0=SIG_EVENT_REBASE_PAUSED)
        | Q(topic_0=SIG_EVENT_REBASE_UNPAUSED)
    ).order_by('block_number')


def run_trigger(new_logs):
    """ Template trigger """
    events = []

    for ev in get_pause_events(new_logs):
        is_pause = ev.topic_0 == SIG_EVENT_REBASE_PAUSED

        events.append(
            event_high(
                "Rebases Paused   ⏸️" if is_pause else "Rebases Unpaused   ▶️",
                "OUSD Vault rebases have been {}".format(
                    "paused" if is_pause else "unpaused",
                ),
                block_number=ev.block_number,
                transaction_index=ev.transaction_index,
                log_index=ev.log_index
            )
        )

    return events
