from decimal import Decimal
from eth_hash.auto import keccak
from eth_abi import decode_single
from eth_utils import encode_hex, decode_hex
from django.db.models import Q
from core.common import format_ousd_human
from core.blockchain import OGN_STAKING, SIG_EVENT_STAKED, SIG_EVENT_WITHDRAWN
from notify.events import event_normal


def get_stake_withdrawn_events(logs):
    """ Get Stake/Withdrawn events """
    return logs.filter(
        Q(address=OGN_STAKING)
        & Q(
            Q(topic_0=SIG_EVENT_STAKED)
            | Q(topic_0=SIG_EVENT_WITHDRAWN)
        )
    ).order_by('block_number')


def run_trigger(new_logs):
    """ Look for Stake/Withdraw """
    events = []

    for ev in get_stake_withdrawn_events(new_logs):
        is_staked = ev.topic_0 == SIG_EVENT_STAKED
        (amount,) = decode_single('(uint256)', decode_hex(ev.data))

        events.append(
            event_normal(
                "Staked    🥩" if is_staked else "Withdrawn 🍰",
                "{} OGN was {}".format(
                    format_ousd_human(Decimal(amount) / Decimal(1e18)),
                    "staked" if is_staked else "withdrawn",
                )
            )
        )

    return events
