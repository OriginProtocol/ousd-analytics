""" Trigger for timelock transactions """
from datetime import datetime
from eth_utils import decode_hex
from eth_abi import decode_single
from django.db.models import Q

from core.blockchain.addresses import (
    CONTRACT_ADDR_TO_NAME,
    COMPOUND_TIMELOCK,
    FLUX_TIMELOCK,
)
from core.blockchain.decode import decode_call
from core.blockchain.sigs import (
    SIG_EVENT_CANCEL_TRANSACTION,
    SIG_EVENT_EXECUTE_TRANSACTION,
    SIG_EVENT_QUEUE_TRANSACTION,
)
from notify.events import event_high


def get_events(logs):
    """ Get events """
    return logs.filter(address__in=[COMPOUND_TIMELOCK, FLUX_TIMELOCK]).filter(
        Q(topic_0=SIG_EVENT_CANCEL_TRANSACTION)
        | Q(topic_0=SIG_EVENT_EXECUTE_TRANSACTION)
        | Q(topic_0=SIG_EVENT_QUEUE_TRANSACTION)
    ).order_by('block_number')


def run_trigger(new_logs):
    """ Trigger events on Compound and Flux Timelock transaction events """
    events = []

    for ev in get_events(new_logs):
        summary = "ERROR"
        action = "ERROR"

        contract_name = CONTRACT_ADDR_TO_NAME.get(ev.address, ev.address)

        if ev.topic_0 == SIG_EVENT_QUEUE_TRANSACTION:
            summary = "{} transaction queued   ⏲️ 📥".format(contract_name)
            action = "queued"
        elif ev.topic_0 == SIG_EVENT_CANCEL_TRANSACTION:
            summary = "{} transaction canceled   ⏲️ ❌".format(contract_name)
            action = "canceled"
        elif ev.topic_0 == SIG_EVENT_EXECUTE_TRANSACTION:
            summary = "{} transaction executed   ⏲️ 🏃‍♀️".format(contract_name)
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
            "{} transaction has been {}\n\n"
            "**Target**: {}\n"
            "**ETA**: {} UTC\n"
            "**Call**: {}".format(
                contract_name,
                action,
                CONTRACT_ADDR_TO_NAME.get(target, target),
                eta,
                call,
            ),
            log_model=ev
        ))

    return events
