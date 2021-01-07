""" Proxy upgrades """
from django.db.models import Q
from eth_utils import decode_hex
from eth_abi import decode_single

from core.blockchain import CONTRACT_ADDR_TO_NAME
from core.sigs import SIG_EVENT_UPGRADED
from notify.events import event_high


def get_events(logs):
    """ Get relevant events """
    return logs.filter(topic_0=SIG_EVENT_UPGRADED).order_by('block_number')


def run_trigger(new_logs):
    """ Trigger on proxy upgrades """
    events = []

    for ev in get_events(new_logs):
        implementation = decode_single('(address)', decode_hex(ev.topic_1))[0]
        contract = CONTRACT_ADDR_TO_NAME.get(ev.address, ev.address)

        events.append(event_high(
            "{} has been upgraded   🆙".format(contract),
            "**Proxy**: {}\n"
            "**New implementation**: {}\n".format(ev.address, implementation)
        ))

    return events
