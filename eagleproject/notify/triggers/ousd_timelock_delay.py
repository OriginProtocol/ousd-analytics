""" Trigger for timelock delay changes """
from datetime import timedelta
from eth_utils import decode_hex
from eth_abi import decode_single

from core.blockchain.addresses import GOVERNANCE_TIMELOCK
from core.blockchain.sigs import SIG_EVENT_MIN_DELAY_CHANGED
from notify.events import event_high


def get_events(logs):
    """ Get NewDelay events """
    return logs.filter(address=GOVERNANCE_TIMELOCK).filter(
        topic_0=SIG_EVENT_MIN_DELAY_CHANGED
    ).order_by('block_number')


def run_trigger(new_logs):
    """ OUSD Timelock delay changes """
    events = []

    for ev in get_events(new_logs):
        old_delay, new_delay = decode_single('(uint256,uint256)', decode_hex(ev.data))
        old_delay_time = timedelta(seconds=old_delay)
        new_delay_time = timedelta(seconds=new_delay)

        events.append(event_high(
            "OUSD Timelock min delay changed   👮",
            "OUSD Timelock min delay has been changed from {} to {}".format(
                old_delay_time, new_delay_time
            ),
            log_model=ev
        ))

    return events
