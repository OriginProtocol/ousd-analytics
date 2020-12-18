from decimal import Decimal
from eth_hash.auto import keccak
from eth_abi import decode_single
from eth_utils import encode_hex, decode_hex
from django.db.models import Q
from core.common import format_ousd_human
from notify.events import event_normal

SIG_EVENT_MINT = encode_hex(keccak(b"Mint(address,uint256)"))
SIG_EVENT_REDEEM = encode_hex(keccak(b"Redeem(address,uint256)"))


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
                )
            )
        )

    return events
