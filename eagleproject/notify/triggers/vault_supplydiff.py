""" Vault UnswapUpdated event trigger """
from decimal import Decimal
from eth_utils import decode_hex
from eth_abi import decode_single

from core.blockchain.sigs import SIG_EVENT_MAX_SUPPLY_DIFF
from notify.events import event_high

from core.blockchain.addresses import CONTRACT_ADDR_TO_NAME

def get_events(logs):
    """ Get events """
    return logs.filter(topic_0=SIG_EVENT_MAX_SUPPLY_DIFF).order_by('block_number')


def run_trigger(new_logs):
    """ Template trigger """
    events = []

    for ev in get_events(new_logs):
        diff = decode_single('(uint256)', decode_hex(ev.data))[0]
        contract_name = CONTRACT_ADDR_TO_NAME.get(ev.address, ev.address)

        events.append(event_high(
            "{} Max Supply Differential Changed   🔢".format(contract_name),
            "Vault supply differential limiter has been changed to {}".format(
                Decimal(diff) / Decimal(1e18)
            ),
            log_model=ev
        ))

    return events
