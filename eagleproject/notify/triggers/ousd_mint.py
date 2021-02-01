from decimal import Decimal
from eth_abi import decode_single
from eth_utils import decode_hex
from django.db.models import Q
from core.common import format_ousd_human
from core.blockchain.sigs import SIG_EVENT_MINT, SIG_EVENT_REDEEM
from notify.events import event_normal


def get_mint_redeem_events(logs):
    """ Get Mint/Redeem events """
    return logs.filter(
        Q(topic_0=SIG_EVENT_MINT)
        | Q(topic_0=SIG_EVENT_REDEEM)
    ).order_by('block_number')


def run_trigger(new_logs):
    """ Look for mints and redeems """
    events = []

    for ev in get_mint_redeem_events(new_logs):
        is_mint = ev.topic_0 == SIG_EVENT_MINT
        addr, value = decode_single('(address,uint256)', decode_hex(ev.data))

        events.append(
            event_normal(
                "Mint   🪙" if is_mint else "Redeem   💵",
                "{} OUSD was {}".format(
                    format_ousd_human(Decimal(value) / Decimal(1e18)),
                    "minted" if is_mint else "redeemed",
                ),
                log_model=ev
            )
        )

    return events
