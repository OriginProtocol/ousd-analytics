from eth_hash.auto import keccak
from eth_utils import encode_hex
from eth_abi import decode_single
from django.db.models import Q
from notify.events import event_high

SIG_EVENT_PAUSED = encode_hex(keccak(b"Paused(address indexed,bool)"))
FALSE_256BIT = "0x0000000000000000000000000000000000000000000000000000000000000000"
TRUE_256BIT = "0x0000000000000000000000000000000000000000000000000000000000000001"


def get_pause_events(logs):
    """ Get DepositsPaused/DepositsUnpaused events """
    return logs.filter(topic_0=SIG_EVENT_PAUSED).order_by('block_number')


def run_trigger(new_logs):
    """ Template trigger """
    events = []

    for ev in get_pause_events(new_logs):
        address = decode_single("(address)", ev.topic_1)
        is_pause = ev.data == TRUE_256BIT

        events.append(
            event_high(
                "Pause   ⏸️" if is_pause else "Unpause   ▶️",
                "OGN Staking was {} by {}".format(
                    "paused" if is_pause else "unpaused",
                    address,
                )
            )
        )

    return events
