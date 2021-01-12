from decimal import Decimal
from eth_abi import decode_single
from eth_utils import decode_hex
from django.db.models import Q
from core.common import format_ousd_human
from core.sigs import (
    SIG_EVENT_MINT,
    SIG_EVENT_REDEEM,
    SIG_EVENT_TOTAL_SUPPLY_UPDATED,
)
from notify.events import event_normal


def get_supply_events(logs):
    """ Get totalSupply changing events """
    return logs.filter(
        topic_0=SIG_EVENT_TOTAL_SUPPLY_UPDATED
    ).order_by('block_number')


def has_mint_or_burn(logs, tx_hash):
    """ Check if the transaction also has a mint or burn event """
    return logs.filter(transaction_hash=tx_hash).filter(
        Q(topic_0=SIG_EVENT_MINT)
        | Q(topic_0=SIG_EVENT_REDEEM)
    ).count() > 0


def run_trigger(new_logs):
    """ Look for mints and redeems """
    events = []

    for ev in get_supply_events(new_logs):
        if has_mint_or_burn(new_logs, ev.transaction_hash):
            continue

        (
            total_supply,
            rebasing_credits,
            rebasing_credits_per_token
        ) = decode_single(
            '(uint256,uint256,uint256)',
            decode_hex(ev.data)
        )

        events.append(
            event_normal(
                "Total supply updated   👛",
                "Total supply is now {} OUSD".format(
                    format_ousd_human(Decimal(total_supply) / Decimal(1e18)),
                )
            )
        )

    return events
