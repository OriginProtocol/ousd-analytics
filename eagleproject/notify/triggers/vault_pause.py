""" NOTE: DepositsPaused and DepositsUnpaused have been depreciated """
from eth_hash.auto import keccak
from eth_utils import encode_hex
from django.db.models import Q
from notify.events import event_high

SIG_EVENT_DEPOSITS_PAUSED = encode_hex(keccak(b"DepositsPaused()"))
SIG_EVENT_DEPOSITS_UNPAUSED = encode_hex(keccak(b"DepositsUnpaused()"))


def get_pause_events(logs):
    """ Get DepositsPaused/DepositsUnpaused events """
    return logs.filter(
        Q(topic_0=SIG_EVENT_DEPOSITS_PAUSED)
        | Q(topic_0=SIG_EVENT_DEPOSITS_UNPAUSED)
    ).order_by('block_number')


def run_trigger(new_logs):
    """ Template trigger """
    events = []

    for ev in get_pause_events(new_logs):
        is_pause = ev.topic_0 == SIG_EVENT_DEPOSITS_PAUSED

        events.append(
            event_high(
                "Pause   ⏸️" if is_pause else "Unpause   ▶️",
                "OUSD Vault was {}".format(
                    "paused" if is_pause else "unpaused",
                )
            )
        )

    return events
