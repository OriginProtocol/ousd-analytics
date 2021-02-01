""" Vault fee related events """
from eth_utils import decode_hex
from eth_abi import decode_single
from django.db.models import Q

from core.blockchain.sigs import (
    SIG_EVENT_ALLOCATE_THRESHOLD,
    SIG_EVENT_REBASE_THRESHOLD,
)
from notify.events import event_normal


def get_events(logs):
    """ Get events """
    return logs.filter(
        Q(topic_0=SIG_EVENT_ALLOCATE_THRESHOLD)
        | Q(topic_0=SIG_EVENT_REBASE_THRESHOLD)
    ).order_by('block_number')


def run_trigger(new_logs):
    """ Template trigger """
    events = []

    for ev in get_events(new_logs):
        threshold = decode_single('(uint256)', decode_hex(ev.data))[0]

        if ev.topic_0 == SIG_EVENT_ALLOCATE_THRESHOLD:
            events.append(event_normal(
                "Vault Allocate Threshold Changed   🥧",
                "OUSD Vault allocation deposit threshold was changed to {} "
                "units".format(threshold),
                log_model=ev
            ))

        elif ev.topic_0 == SIG_EVENT_REBASE_THRESHOLD:
            events.append(event_normal(
                "Vault Rebase Threshold Changed   🍱",
                "OUSD Vault rebase threshold was changed to {} "
                "units".format(threshold),
                log_model=ev
            ))

        else:
            raise Exception("You never saw this")

    return events
