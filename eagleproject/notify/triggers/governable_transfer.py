""" Governable transfers of governorship """
from django.db.models import Q
from eth_utils import decode_hex
from eth_abi import decode_single

from core.blockchain.sigs import SIG_EVENT_PENDING_TRANSFER, SIG_EVENT_TRANSFER
from notify.events import event_high


def get_events(logs):
    """ Get relevant events """
    return logs.filter(
        Q(topic_0=SIG_EVENT_PENDING_TRANSFER)
        | Q(topic_0=SIG_EVENT_TRANSFER)
    ).order_by('block_number')


def run_trigger(new_logs):
    """ Trigger on governorship transfers """
    events = []

    for ev in get_events(new_logs):
        former_governor = decode_single('(address)', decode_hex(ev.topic_1))[0]
        new_governor = decode_single('(address)', decode_hex(ev.topic_2))[0]

        if ev.topic_0 == SIG_EVENT_PENDING_TRANSFER:
            events.append(event_high(
                "New proxy governor pending   👮🔄",
                "**Contract**: {}\n"
                "**Current governor**: {}\n"
                "**Proposed governor**: {}".format(
                    ev.address,
                    former_governor,
                    new_governor
                ),
                log_model=ev
            ))

        if ev.topic_0 == SIG_EVENT_TRANSFER:
            events.append(event_high(
                "New proxy governor claimed   👮",
                "**Contract**: {}\n"
                "**Former governor**: {}\n"
                "**New governor**: {}".format(
                    ev.address,
                    former_governor,
                    new_governor
                ),
                log_model=ev
            ))

    return events
