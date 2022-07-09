from django.db.models import Q
from notify.events import event_high

from core.blockchain.addresses import STORY_STAKING_VAULT
from core.blockchain.sigs import SIG_EVENT_OZ_PAUSED, SIG_EVENT_OZ_UNPAUSED


def get_pause_events(logs):
    """ Get Paused/Unpaused events """
    return logs.filter(
        Q(address=STORY_STAKING_VAULT)
        & Q(Q(topic_0=SIG_EVENT_OZ_PAUSED) | Q(topic_0=SIG_EVENT_OZ_UNPAUSED))
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
                log_model=ev,
            )
        )

    return events
