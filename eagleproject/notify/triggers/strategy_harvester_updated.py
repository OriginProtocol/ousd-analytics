from eth_utils import decode_hex
from eth_abi import decode_single

from core.blockchain.addresses import (
    CONTRACT_ADDR_TO_NAME,
)
from core.common import format_token_human
from core.blockchain.sigs import SIG_EVENT_HARVESTER_UPDATED
from notify.events import event_normal


def get_events(logs):
    """ Get events """
    return logs.filter(topic_0=SIG_EVENT_HARVESTER_UPDATED).order_by(
        "block_number"
    )


def run_trigger(new_logs):
    """ Template trigger """
    events = []

    for ev in get_events(new_logs):
        prev_harvester, new_harvester = decode_single(
            "(address,address)", decode_hex(ev.data)
        )

        contract_name = CONTRACT_ADDR_TO_NAME.get(ev.address, ev.address)

        events.append(
            event_normal(
                "Harvester Address Updated   💸",
                "Harvester changed from {} to {} on {} contract\n".format(
                    prev_harvester,
                    new_harvester,
                    contract_name,
                ),
                log_model=ev,
            )
        )

    return events
