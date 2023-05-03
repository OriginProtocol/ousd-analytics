""" RebasePaused/RebaseUnpaused events """
from django.db.models import Q
from core.blockchain.sigs import (
    SIG_EVENT_REBASE_PAUSED,
    SIG_EVENT_REBASE_UNPAUSED,
)
from notify.events import event_high

from core.blockchain.addresses import CONTRACT_ADDR_TO_NAME


def get_pause_events(logs):
    """ Get RebasePaused/RebaseUnpaused events """
    return logs.filter(
        Q(topic_0=SIG_EVENT_REBASE_PAUSED)
        | Q(topic_0=SIG_EVENT_REBASE_UNPAUSED)
    ).order_by('block_number')


def run_trigger(new_logs):
    """ Template trigger """
    events = []

    for ev in get_pause_events(new_logs):
        is_pause = ev.topic_0 == SIG_EVENT_REBASE_PAUSED
        contract_name = CONTRACT_ADDR_TO_NAME.get(ev.address, ev.address)

        events.append(
            event_high(
                "Rebases Paused   ⏸️" if is_pause else "Rebases Unpaused   ▶️",
                "{} rebases have been {}".format(
                    contract_name,
                    "paused" if is_pause else "unpaused",
                ),
                log_model=ev
            )
        )

    return events
