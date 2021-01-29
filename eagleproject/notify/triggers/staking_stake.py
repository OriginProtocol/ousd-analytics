from datetime import timedelta
from decimal import Decimal
from eth_abi import decode_single
from eth_utils import decode_hex
from django.db.models import Q
from core.common import format_ousd_human
from core.models import OgnStaked
from core.blockchain.addresses import OGN_STAKING
from core.blockchain.sigs import (
    SIG_EVENT_STAKED,
    SIG_EVENT_WITHDRAWN,
    DEPRECATED_SIG_EVENT_STAKED,
    DEPRECATED_SIG_EVENT_WITHDRAWN,
)
from core.logging import get_logger
from notify.events import event_normal
from notify.triggers.staking_rates import DAYS_365_SECONDS

log = get_logger(__name__)


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
                    ),
                    block_number=ev.block_number,
                    transaction_index=ev.transaction_index,
                    log_index=ev.log_index
                )
            )
        elif ev.topic_0 == SIG_EVENT_STAKED:
            verb = 'staked'

            amount, duration, rate = decode_single(
                '(uint256,uint256,uint256)',
                decode_hex(ev.data)
            )
            stakes = OgnStaked.objects.filter(tx_hash=ev.transaction_hash)

            # There should be a stake in the DB
            if len(stakes) < 1:
                log.warning('No stakes found in DB')

            # Non-standard stake types
            elif stakes[0].stake_type == 1:
                verb = 'claimed as compensation and staked'

            # Currently unused
            else:
                log.warning('Unsupported stake_type {}'.format(
                    stakes[0].stake_type
                ))

            duration_dt = timedelta(seconds=duration)

            apy_multiple = Decimal(DAYS_365_SECONDS) / Decimal(duration)
            apy = round((Decimal(rate) / Decimal(1e18)) * apy_multiple * Decimal(100), 1)

            events.append(
                event_normal(
                    "Staked    🥩",
                    "{} OGN was {} for {} days at {}%".format(
                        format_ousd_human(Decimal(amount) / Decimal(1e18)),
                        verb,
                        duration_dt.days,
                        apy
                    ),
                    block_number=ev.block_number,
                    transaction_index=ev.transaction_index,
                    log_index=ev.log_index
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
                    ),
                    block_number=ev.block_number,
                    transaction_index=ev.transaction_index,
                    log_index=ev.log_index
                )
            )

    return events
