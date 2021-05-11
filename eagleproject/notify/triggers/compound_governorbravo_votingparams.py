""" Trigger for GovernorBravo voting parameter change """
from decimal import Decimal
from django.db.models import Q
from eth_utils import decode_hex
from eth_abi import decode_single

from core.blockchain.addresses import COMPOUND_GOVERNOR_BRAVO
from core.blockchain.const import E_18
from core.blockchain.sigs import (
    SIG_EVENT_VOTING_DELAY_SET,
    SIG_EVENT_VOTING_PERIOD_SET,
    SIG_EVENT_PROPOSAL_THRESHOLD_SET,
)
from notify.events import event_normal

DISCORD_EMBED_DESCRIPTION_LIMIT = 2048


def get_events(logs):
    """ Get Mint/Redeem events """
    return logs.filter(address=COMPOUND_GOVERNOR_BRAVO).filter(
        Q(topic_0=SIG_EVENT_VOTING_DELAY_SET)
        | Q(topic_0=SIG_EVENT_VOTING_PERIOD_SET)
        | Q(topic_0=SIG_EVENT_PROPOSAL_THRESHOLD_SET)
    ).order_by('block_number')


def run_trigger(new_logs):
    """ Compound Timelock changes """
    events = []

    for ev in get_events(new_logs):
        if ev.topic_0 == SIG_EVENT_VOTING_DELAY_SET:
            old_delay, new_delay = decode_single(
                "(uint256,uint256)",
                decode_hex(ev.data)
            )

            events.append(event_normal(
                "Compound GovernorBravo voting delay changed   🗳️ 🕖",
                "Compound GovernorBravo voting delay changed from {} blocks to {} blocks".format(
                    old_delay, new_delay
                ),
                log_model=ev
            ))

        elif ev.topic_0 == SIG_EVENT_VOTING_PERIOD_SET:
            old_period, new_period = decode_single(
                "(uint256,uint256)",
                decode_hex(ev.data)
            )

            events.append(event_normal(
                "Compound GovernorBravo voting delay changed   🗳️ 🕗",
                "Compound GovernorBravo voting period changed from {} blocks to {} blocks".format(
                    old_period, new_period
                ),
                log_model=ev
            ))

        elif ev.topic_0 == SIG_EVENT_PROPOSAL_THRESHOLD_SET:
            old_threshold, new_threshold = decode_single(
                "(uint256,uint256)",
                decode_hex(ev.data)
            )

            old_human = Decimal(old_threshold) / E_18
            new_human = Decimal(new_threshold) / E_18

            events.append(event_normal(
                "Compound GovernorBravo voting threshold changed   🗳️ 🪙",
                "Compound GovernorBravo voting threshold changed from {} COMP to {} COMP".format(
                    old_human, new_human
                ),
                log_model=ev
            ))

    return events
