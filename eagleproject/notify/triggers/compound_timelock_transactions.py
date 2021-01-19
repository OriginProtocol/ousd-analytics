""" Trigger for timelock transactions """
from datetime import datetime
from eth_utils import decode_hex
from eth_abi import decode_single
from django.db.models import Q

from core.blockchain.addresses import CONTRACT_ADDR_TO_NAME, COMPOUND_TIMELOCK
from core.blockchain.decode import decode_call
from core.blockchain.sigs import (
    SIG_EVENT_CANCEL_TRANSACTION,
    SIG_EVENT_EXECUTE_TRANSACTION,
    SIG_EVENT_QUEUE_TRANSACTION,
)
from notify.events import event_high


def get_events(logs):
    """ Get events """
    return logs.filter(address=COMPOUND_TIMELOCK).filter(
        Q(topic_0=SIG_EVENT_CANCEL_TRANSACTION)
        | Q(topic_0=SIG_EVENT_EXECUTE_TRANSACTION)
        | Q(topic_0=SIG_EVENT_QUEUE_TRANSACTION)
    ).order_by('block_number')


def run_trigger(new_logs):
    """ Trigger events on Compound Timelock transaction events """
    events = []

    for ev in get_events(new_logs):
        summary = "ERROR"
        action = "ERROR"

        if ev.topic_0 == SIG_EVENT_QUEUE_TRANSACTION:
            summary = "Compound Timelock transaction queued   ⏲️ 📥"
            action = "queued"
        elif ev.topic_0 == SIG_EVENT_CANCEL_TRANSACTION:
            summary = "Compound Timelock transaction canceled   ⏲️ ❌"
            action = "canceled"
        elif ev.topic_0 == SIG_EVENT_EXECUTE_TRANSACTION:
            summary = "Compound Timelock transaction executed   ⏲️ 🏃‍♀️"
            action = "executed"

        # They all have the same args so most of thise can be reused
        # tx_hash = decode_single("(bytes32)", decode_hex(ev.topic_1))[0]
        target = decode_single("(address)", decode_hex(ev.topic_2))[0]
        value, signature, data, eta_stamp = decode_single(
            "(uint256,string,bytes,uint256)",
            decode_hex(ev.data)
        )

        eta = datetime.utcfromtimestamp(eta_stamp)
        call = decode_call(signature, data)

        events.append(event_high(
            summary,
            "Compound Timelock transaction has been {}\n\n"
            "**Target**: {}\n"
            "**ETA**: {} UTC\n"
            "**Call**: {}".format(
                action,
                CONTRACT_ADDR_TO_NAME.get(target, target),
                eta,
                call,
            )
        ))

    return events
