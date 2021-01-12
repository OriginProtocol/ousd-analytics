""" Vault fee related events """
from decimal import Decimal
from eth_utils import decode_hex
from eth_abi import decode_single
from core.sigs import SIG_EVENT_REDEEM_FEE
from notify.events import event_normal


def get_events(logs):
    """ Get events """
    return logs.filter(
        topic_0=SIG_EVENT_REDEEM_FEE
    ).order_by('block_number')


def run_trigger(new_logs):
    """ Template trigger """
    events = []

    for ev in get_events(new_logs):
        # Basis points in 18 decimal bigint
        bps_int = decode_single('(uint256)', decode_hex(ev.data))[0]
        bps = Decimal(bps_int) / Decimal(10000)

        events.append(event_normal(
            "Vault Redeem Fee Updated   🦴",
            "OUSD Vault redeem fee was changed to {}%".format(bps)
        ))

    return events
