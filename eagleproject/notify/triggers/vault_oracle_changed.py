""" Vault fee related events """
from eth_utils import decode_hex
from eth_abi import decode_single
from core.blockchain.sigs import SIG_EVENT_PRICE_PROVIDER
from notify.events import event_normal

from core.blockchain.addresses import CONTRACT_ADDR_TO_NAME

def get_events(logs):
    """ Get events """
    return logs.filter(
        topic_0=SIG_EVENT_PRICE_PROVIDER
    ).order_by('block_number')


def run_trigger(new_logs):
    """ Template trigger """
    events = []

    for ev in get_events(new_logs):
        # Basis points in 18 decimal bigint
        oracle_address = decode_single('(address)', decode_hex(ev.data))[0]
        contract_name = CONTRACT_ADDR_TO_NAME.get(ev.address, ev.address)

        events.append(event_normal(
            "{} Oracle Changed   🧙".format(contract_name),
            "{} oracle was changed to {}%".format(contract_name, oracle_address),
            log_model=ev
        ))

    return events
