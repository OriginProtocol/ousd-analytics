""" Vault UnswapUpdated event trigger """
from eth_utils import decode_hex
from eth_abi import decode_single

from core.blockchain.sigs import SIG_EVENT_UNISWAP
from core.blockchain.addresses import OGV_BUYBACK_LEGACY, OGV_BUYBACK_PROXY, CONTRACT_ADDR_TO_NAME
from notify.events import event_normal


def get_events(logs):
    """ Get events """
    return logs.filter(topic_0=SIG_EVENT_UNISWAP).order_by('block_number')


def run_trigger(new_logs):
    """ Template trigger """
    events = []

    for ev in get_events(new_logs):
        uniswap_address = decode_single('(address)', decode_hex(ev.data))[0]
        uniswap_version = "V3" if ev.address in [OGV_BUYBACK_LEGACY, OGV_BUYBACK_PROXY] else "V2"
        contract_name = CONTRACT_ADDR_TO_NAME.get(ev.address, ev.address)
        events.append(event_normal(
            "{} Uniswap {} Router Address Changed   🦄".format(contract_name, uniswap_version),
            "Uniswap {} Router was changed to {} ".format(uniswap_version, uniswap_address),
            log_model=ev
        ))

    return events
