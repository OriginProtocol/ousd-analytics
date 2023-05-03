from django.db.models import Q
from core.blockchain.sigs import (
    SIG_EVENT_CAPITAL_PAUSED,
    SIG_EVENT_CAPITAL_UNPAUSED,
)
from notify.events import event_high
from core.blockchain.addresses import CONTRACT_ADDR_TO_NAME

def get_pause_events(logs):
    """ Get CapitalPaused/CapitalUnpaused events """
    return logs.filter(
        Q(topic_0=SIG_EVENT_CAPITAL_PAUSED)
        | Q(topic_0=SIG_EVENT_CAPITAL_UNPAUSED)
    ).order_by('block_number')


def run_trigger(new_logs):
    """ Template trigger """
    events = []

    for ev in get_pause_events(new_logs):
        is_pause = ev.topic_0 == SIG_EVENT_CAPITAL_PAUSED
        contract_name = CONTRACT_ADDR_TO_NAME.get(ev.address, ev.address)

        events.append(
            event_high(
                "Capital Paused   ⏸️" if is_pause else "Capital Unpaused   ▶️",
                "{} capital has been {}".format(
                    contract_name,
                    "paused" if is_pause else "unpaused",
                ),
                log_model=ev
            )
        )

    return events
