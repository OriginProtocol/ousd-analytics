from notify.events import event_high

from core.blockchain.addresses import STORY_STAKING_VAULT
from core.blockchain.sigs import SIG_EVENT_OZ_PAUSED, SIG_EVENT_OZ_UNPAUSED

EVENT_TAGS = ["ogn"]


def get_pause_events(logs):
    """ Get Paused/Unpaused events """
    return logs.filter(
        address=STORY_STAKING_VAULT,
        topic_0__in=[SIG_EVENT_OZ_PAUSED, SIG_EVENT_OZ_UNPAUSED],
    ).order_by("block_number")


def run_trigger(new_logs):
    """ Template trigger """
    events = []

    for ev in get_pause_events(new_logs):
        is_pause = ev.topic_0 == SIG_EVENT_OZ_PAUSED

        events.append(
            event_high(
                "Pause   ⏸️" if is_pause else "Unpause   ▶️",
                "FeeVault was {}".format(
                    "paused" if is_pause else "unpaused",
                ),
                tags=EVENT_TAGS,
                log_model=ev,
            )
        )

    return events
