from decimal import Decimal
from eth_abi import decode_single
from eth_utils import decode_hex
from django.db.models import Q
from core.common import format_ousd_human
from core.blockchain.addresses import OUSD, OETH
from core.blockchain.const import E_18
from core.blockchain.rpc import totalSupply
from core.blockchain.sigs import (
    SIG_EVENT_MINT,
    SIG_EVENT_REDEEM,
    SIG_EVENT_TOTAL_SUPPLY_UPDATED,
    SIG_EVENT_TOTAL_SUPPLY_UPDATED_HIRES,
)
from notify.events import event_normal

def get_supply_events(logs):
    """Get totalSupply changing events

    Original event:

    TotalSupplyUpdated(
        uint256 totalSupply,
        uint256 rebasingCredits,
        uint256 rebasingCreditsPerToken
    )

    New event with resolution upgade:

    TotalSupplyUpdatedHighres(
        uint256 totalSupply,
        uint256 rebasingCredits,
        uint256 rebasingCreditsPerToken
    )
    """
    return logs.filter(
        Q(topic_0=SIG_EVENT_TOTAL_SUPPLY_UPDATED)
        | Q(topic_0=SIG_EVENT_TOTAL_SUPPLY_UPDATED_HIRES)
    ).order_by("block_number")


def has_mint_or_burn(logs, tx_hash):
    """ Check if the transaction also has a mint or burn event """
    return (
        logs.filter(transaction_hash=tx_hash)
        .filter(Q(topic_0=SIG_EVENT_MINT) | Q(topic_0=SIG_EVENT_REDEEM))
        .count()
        > 0
    )


def run_trigger(new_logs):
    """ Look for mints and redeems """
    events = []

    for ev in get_supply_events(new_logs):
        if has_mint_or_burn(new_logs, ev.transaction_hash):
            continue

        if not ev.address in (OETH, OUSD):
            continue

        token_symbol = "OUSD" if ev.address == OUSD else "OETH"

        (
            total_supply,
            rebasing_credits,
            rebasing_credits_per_token,
        ) = decode_single("(uint256,uint256,uint256)", decode_hex(ev.data))

        total_supply_converted = Decimal(total_supply) / E_18
        prev_total_supply = totalSupply(ev.address, 18, block=ev.block_number - 1)
        diff = Decimal(total_supply_converted - prev_total_supply)

        mod = "+"
        if total_supply < prev_total_supply:
            mod = "-"

        events.append(
            event_normal(
                "{} Total supply updated   👛".format(token_symbol),
                "Total supply is now {} {} ({}{} {})".format(
                    format_ousd_human(total_supply_converted),
                    token_symbol,
                    mod,
                    format_ousd_human(diff),
                    token_symbol,
                ),
                log_model=ev,
            ),
        )

    return events
