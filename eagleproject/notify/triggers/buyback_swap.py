""" BuyBack swap event triggers """
from eth_utils import decode_hex
from eth_abi import decode_single

from core.models import Log

from core.blockchain.addresses import OGV, OGV_BUYBACK, REWARDS_SOURCE, OUSD
from core.blockchain.sigs import TRANSFER
from core.common import format_token_human
from notify.events import event_low


def get_events(logs):
    """ Get events """
    return logs.filter(address=OUSD,topic_0=TRANSFER,topic_1=get_long_address(OGV_BUYBACK)).order_by('block_number')

def run_trigger(new_logs):
    """ Template trigger """
    events = []

    for ev in get_events(new_logs):
        swap_log = get_ogv_swap_log(ev.transaction_hash)

        if swap_log is None:
            continue

        ousd_out = decode_single('(uint256)',decode_hex(ev.data))[0]
        ogv_in = decode_single('(uint256)',decode_hex(swap_log.data))[0]

        events.append(event_low(
            "OGV BuyBack        🔄",
            "Swapped {} OUSD for {} OGV and depositted to Rewards Source contract".format(
                format_token_human('OUSD', ousd_out), 
                format_token_human('OGV', ogv_in),
            ),
            log_model=ev
        ))

    return events

def get_ogv_swap_log(transaction_hash):
    return Log.objects.get(transaction_hash=transaction_hash,address=OGV,topic_2=get_long_address(REWARDS_SOURCE))

def get_long_address(address):
    return address.replace("0x", "0x000000000000000000000000")
