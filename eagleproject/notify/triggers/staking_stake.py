from decimal import Decimal
from eth_abi import decode_single
from eth_utils import decode_hex
from django.db.models import Q
from core.common import format_ousd_human
from core.blockchain.addresses import OGN_STAKING
from core.blockchain import (
    SIG_EVENT_STAKED,
    SIG_EVENT_WITHDRAWN,
    DEPRECATED_SIG_EVENT_STAKED,
    DEPRECATED_SIG_EVENT_WITHDRAWN,
)
from notify.events import event_normal
from datetime import timedelta
from notify.triggers.staking_rates import DAYS_365_SECONDS


def get_stake_withdrawn_events(logs):
    """ Get Stake/Withdrawn events """
    return logs.filter(
        Q(address=OGN_STAKING)
        & Q(
            Q(topic_0=SIG_EVENT_STAKED)
            | Q(topic_0=SIG_EVENT_WITHDRAWN)
            | Q(topic_0=DEPRECATED_SIG_EVENT_STAKED)
            | Q(topic_0=DEPRECATED_SIG_EVENT_WITHDRAWN)
        )
    ).order_by('block_number')


def run_trigger(new_logs):
    """ Look for Stake/Withdraw """
    events = []

    for ev in get_stake_withdrawn_events(new_logs):

        if (
            ev.topic_0 == DEPRECATED_SIG_EVENT_STAKED
            or ev.topic_0 == DEPRECATED_SIG_EVENT_WITHDRAWN
        ):
            is_staked = ev.topic_0 == DEPRECATED_SIG_EVENT_STAKED

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
        elif ev.topic_0 == SIG_EVENT_STAKED:
            amount, duration, rate = decode_single(
                '(uint256,uint256,uint256)',
                decode_hex(ev.data)
            )

            duration_dt = timedelta(seconds=duration)

            apy_multiple = Decimal(DAYS_365_SECONDS) / Decimal(duration)
            apy = round((Decimal(rate) / Decimal(1e18)) * apy_multiple * Decimal(100), 1)

            events.append(
                event_normal(
                    "Staked    🥩",
                    "{} OGN was staked for {} days at {}%".format(
                        format_ousd_human(Decimal(amount) / Decimal(1e18)),
                        duration_dt.days,
                        apy
                    )
                )
            )
        elif ev.topic_0 == SIG_EVENT_WITHDRAWN:
            amount,staked_amount = decode_single(
                '(uint256,uint256)',
                decode_hex(ev.data)
            )

            events.append(
                event_normal(
                    "Withdrawn 🍰",
                    "{} OGN was withdrawn".format(
                        format_ousd_human(Decimal(amount) / Decimal(1e18))
                    )
                )
            )

    return events
