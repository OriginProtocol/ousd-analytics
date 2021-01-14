""" Vault UnswapUpdated event trigger """
from eth_utils import decode_hex
from eth_abi import decode_single

from core.blockchain.sigs import SIG_EVENT_UNISWAP
from notify.events import event_normal


def get_events(logs):
    """ Get events """
    return logs.filter(topic_0=SIG_EVENT_UNISWAP).order_by('block_number')


def run_trigger(new_logs):
    """ Template trigger """
    events = []

    for ev in get_events(new_logs):
        address = decode_single('(address)', decode_hex(ev.data))[0]

        events.append(event_normal(
            "Vault Uniswap V2 Router Address Changed   🦄",
            "Uniswap V2 Router was changed to {} ".format(address)
        ))

    return events
