from eth_abi import decode_single
from eth_utils import decode_hex
from django.db.models import Q

from core.blockchain.addresses import STORY_STAKING_VAULT
from core.blockchain.sigs import SIG_EVENT_NEW_CONTROLLER

from notify.events import event_high


def get_pause_events(logs):
    """ Get Paused/Unpaused events """
    return logs.filter(
        Q(address=STORY_STAKING_VAULT) & Q(topic_0=SIG_EVENT_NEW_CONTROLLER)
    ).order_by("block_number")


def run_trigger(new_logs):
    """ Template trigger """
    events = []

    for ev in get_pause_events(new_logs):
        controller = decode_single("(address)", decode_hex(ev.data))[0]

        events.append(
            event_high(
                "New Controller   🛂",
                "FeeVault has a new controller: {}".format(controller),
                log_model=ev,
            )
        )

    return events
