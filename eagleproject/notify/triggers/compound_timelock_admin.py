""" Trigger for timelock admin changes """
from django.db.models import Q
from eth_utils import decode_hex
from eth_abi import decode_single

from core.blockchain.addresses import (
    CONTRACT_ADDR_TO_NAME,
    COMPOUND_TIMELOCK,
    FLUX_TIMELOCK,
)
from core.blockchain.sigs import (
    SIG_EVENT_NEW_ADMIN,
    SIG_EVENT_NEW_PENDING_ADMIN,
)
from notify.events import event_high


def get_events(logs):
    """ Get Mint/Redeem events """
    return logs.filter(address__in=[COMPOUND_TIMELOCK, FLUX_TIMELOCK]).filter(
        Q(topic_0=SIG_EVENT_NEW_ADMIN)
        | Q(topic_0=SIG_EVENT_NEW_PENDING_ADMIN)
    ).order_by('block_number')


def run_trigger(new_logs):
    """ Compound Timelock changes """
    events = []

    for ev in get_events(new_logs):
        admin_address = decode_single("(address)", decode_hex(ev.topic_1))[0]

        contract_name = CONTRACT_ADDR_TO_NAME.get(ev.address, ev.address)

        if ev.topic_0 == SIG_EVENT_NEW_ADMIN:
            events.append(event_high(
                "{} admin claimed   👮".form(contract_name),
                "A new admin has been set for the {} "
                "contract: {}".format(
                    contract_name,
                    admin_address
                ),
                log_model=ev
            ))

        elif ev.topic_0 == SIG_EVENT_NEW_PENDING_ADMIN:
            events.append(event_high(
                "New {} admin proposed   👮".format(contract_name),
                "{} has been proposed as the new admin for the {} "
                "governor contract and is currently waiting to be "
                "claimed.".format(
                    admin_address,
                    contract_name
                ),
                log_model=ev
            ))

    return events
