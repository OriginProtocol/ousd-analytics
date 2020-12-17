from decimal import Decimal
from eth_hash.auto import keccak
from eth_abi import decode_single
from eth_utils import encode_hex, decode_hex
from django.db.models import Q
from core.common import format_ousd_human
from notify.events import event_low

SIG_EVENT_TOTAL_SUPPLY_UPDATED = encode_hex(
    keccak(b"TotalSupplyUpdated(uint256,uint256,uint256)")
)


def get_supply_events(logs):
    """ Get totalSupply changing events """
    return logs.filter(
        topic_0=SIG_EVENT_TOTAL_SUPPLY_UPDATED
    ).order_by('block_number')


def run_trigger(new_logs):
    """ Look for mints and redeems """
    events = []

    for ev in get_supply_events(new_logs):
        (
            total_supply,
            rebasing_credits,
            rebasing_credits_per_token
        ) = decode_single(
            '(uint256,uint256,uint256)',
            decode_hex(ev.data)
        )

        events.append(
            event_low(
                "Total supply updated   👛",
                "Total supply is now {} OUSD".format(
                    format_ousd_human(Decimal(total_supply) / Decimal(1e18)),
                )
            )
        )

    return events
