""" Trigger for timelock admin changes """
from django.db.models import Q
from eth_utils import decode_hex
from eth_abi import decode_single

from core.blockchain.addresses import COMPOUND_TIMELOCK
from core.blockchain.sigs import (
    SIG_EVENT_NEW_ADMIN,
    SIG_EVENT_NEW_PENDING_ADMIN,
)
from notify.events import event_high


def get_events(logs):
    """ Get Mint/Redeem events """
    return logs.filter(address=COMPOUND_TIMELOCK).filter(
        Q(topic_0=SIG_EVENT_NEW_ADMIN)
        | Q(topic_0=SIG_EVENT_NEW_PENDING_ADMIN)
    ).order_by('block_number')


def run_trigger(new_logs):
    """ Compound Timelock changes """
    events = []

    for ev in get_events(new_logs):
        admin_address = decode_single("(address)", decode_hex(ev.topic_1))[0]

        if ev.topic_0 == SIG_EVENT_NEW_ADMIN:
            events.append(event_high(
                "Compound Timelock admin claimed   👮",
                "A new admin has been set for the Compound Timelock "
                "contract: {}".format(
                    admin_address
                )
            ))

        elif ev.topic_0 == SIG_EVENT_NEW_PENDING_ADMIN:
            events.append(event_high(
                "New Compound Timelock admin proposed   👮",
                "{} has been proposed as the new admin for the Compound "
                "Timelock governor contract and is currently waiting to be "
                "claimed.".format(
                    admin_address
                )
            ))

    return events
