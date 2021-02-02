""" Trigger for timelock admin changes """
from datetime import timedelta
from eth_utils import decode_hex
from eth_abi import decode_single

from core.blockchain.addresses import COMPOUND_TIMELOCK
from core.blockchain.sigs import SIG_EVENT_DELAY
from notify.events import event_high


def get_events(logs):
    """ Get NewDelay events """
    return logs.filter(address=COMPOUND_TIMELOCK).filter(
        topic_0=SIG_EVENT_DELAY
    ).order_by('block_number')


def run_trigger(new_logs):
    """ Timelock changes """
    events = []

    for ev in get_events(new_logs):
        delay_seconds = decode_single("(uint256)", decode_hex(ev.topic_1))[0]
        delay = timedelta(seconds=delay_seconds)

        events.append(event_high(
            "Compound Timelock delay changed   👮",
            "Compound Timelock delay has been changed to {}".format(
                delay
            ),
            log_model=ev
        ))

    return events
