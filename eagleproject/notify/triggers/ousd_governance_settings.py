""" Trigger for OUSD Governance additional parameters change """
from django.db.models import Q
from eth_utils import decode_hex
from eth_abi import decode_single

from core.blockchain.addresses import GOVERNANCE
from core.blockchain.sigs import (
    SIG_EVENT_LATE_QUORUM_VOTE_EXTENSION_SET,
    SIG_EVENT_QUORUM_NUMERATOR_UPDATED,
    SIG_EVENT_TIMELOCK_CHANGE,
)
from notify.events import event_normal


def get_events(logs):
    """ Get OUSD Governance Additional Settings changed events """
    return logs.filter(address=GOVERNANCE).filter(
        Q(topic_0=SIG_EVENT_LATE_QUORUM_VOTE_EXTENSION_SET)
        | Q(topic_0=SIG_EVENT_TIMELOCK_CHANGE)
        | Q(topic_0=SIG_EVENT_QUORUM_NUMERATOR_UPDATED)
    ).order_by('block_number')


def run_trigger(new_logs):
    """ OUSD Governance Additional Settings changes """
    events = []

    for ev in get_events(new_logs):
        if ev.topic_0 == SIG_EVENT_LATE_QUORUM_VOTE_EXTENSION_SET:
            old_vote_extension, new_vote_extension = decode_single(
                "(uint64,uint64)",
                decode_hex(ev.data)
            )

            events.append(event_normal(
                "OUSD Governance late quorum vote extension changed   🗳️ 🕖",
                "OUSD Governance late quorum vote extension from {} blocks to {} blocks".format(
                    old_vote_extension, new_vote_extension
                ),
                log_model=ev
            ))

        elif ev.topic_0 == SIG_EVENT_QUORUM_NUMERATOR_UPDATED:
            old_numerator, new_numerator = decode_single(
                "(uint256,uint256)",
                decode_hex(ev.data)
            )

            events.append(event_normal(
                "OUSD Governance quorum numerator changed   🗳️ 🪙",
                "OUSD Governance quorum numerator changed from {} to {}".format(
                    old_numerator, new_numerator
                ),
                log_model=ev
            ))

        elif ev.topic_0 == SIG_EVENT_TIMELOCK_CHANGE:
            old_timelock, new_timelock = decode_single(
                "(address,address)",
                decode_hex(ev.data)
            )

            events.append(event_normal(
                "OUSD Governance timelock address changed   🗳️ 🕗",
                "OUSD Governance timelock address changed from {} to {}".format(
                    old_timelock, new_timelock
                ),
                log_model=ev
            ))

    return events
