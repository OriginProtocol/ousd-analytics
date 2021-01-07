""" Trigger for timelock admin changes """
from datetime import timedelta
from eth_abi import decode_single

from core.sigs import SIG_EVENT_DELAY
from notify.events import event_high


def get_events(logs):
    """ Get NewDelay events """
    return logs.filter(topic_0=SIG_EVENT_DELAY).order_by('block_number')


def run_trigger(new_logs):
    """ Timelock changes """
    events = []

    for ev in get_events(new_logs):
        delay_seconds = decode_single("(uint256)", ev.topic_1)
        delay = timedelta(seconds=delay_seconds)

        events.append(event_high(
            "Timelock delay changed   👮",
            "Timelock delay has been changed to {}".format(
                delay
            )
        ))

    return events
