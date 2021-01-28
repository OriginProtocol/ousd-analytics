from eth_abi import decode_single
from core.blockchain.addresses import OGN_STAKING
from core.blockchain.sigs import SIG_EVENT_STAKING_PAUSED
from core.blockchain.const import TRUE_256BIT
from notify.events import event_high

EVENT_TAGS = ['ogn']


def get_pause_events(logs):
    """ Get DepositsPaused/DepositsUnpaused events """
    return logs.filter(address=OGN_STAKING).filter(
        topic_0=SIG_EVENT_STAKING_PAUSED
    ).order_by('block_number')


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
                ),
                tags=EVENT_TAGS
            )
        )

    return events
