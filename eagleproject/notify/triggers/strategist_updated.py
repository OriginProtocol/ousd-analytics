""" StrategistUpdated event trigger """
from eth_utils import decode_hex
from eth_abi import decode_single

from django.db.models import Q

from core.blockchain.addresses import CONTRACT_ADDR_TO_NAME
from core.blockchain.sigs import SIG_EVENT_STRATEGIST
from notify.events import event_normal


def get_events(logs):
    """ Get events """
    return logs.filter(topic_0=SIG_EVENT_STRATEGIST).order_by('block_number')


def run_trigger(new_logs):
    """ Template trigger """
    events = []

    for ev in get_events(new_logs):
        new_strategist_address = decode_single('(address)', decode_hex(ev.data))[0]

        contract_address = ev.address
        contract_name = CONTRACT_ADDR_TO_NAME.get(contract_address, contract_address)

        events.append(event_normal(
            "{} Strategist Changed   🕴️".format(contract_name),
            "The new {} strategist is {} ".format(contract_name, new_strategist_address),
            log_model=ev
        ))

    return events
