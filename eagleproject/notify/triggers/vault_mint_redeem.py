from decimal import Decimal
from eth_abi import decode_single
from eth_utils import decode_hex
from django.db.models import Q
from core.common import format_ousd_human
from core.blockchain.sigs import SIG_EVENT_MINT, SIG_EVENT_REDEEM
from notify.events import event_normal

from core.blockchain.addresses import CONTRACT_ADDR_TO_NAME, OUSD_VAULT, OETH_VAULT

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
        contract_name = CONTRACT_ADDR_TO_NAME.get(ev.address, ev.address)
        token_symbol = "OUSD" if ev.address == OUSD_VAULT else "OETH"
        dec_places = 4 if ev.address == OUSD_VAULT else 8 

        events.append(
            event_normal(
                "{} Mint   🪙".format(token_symbol) if is_mint else "{} Redeem   💵".format(token_symbol),
                "{} {} was {}".format(
                    format_ousd_human(Decimal(value) / Decimal(1e18), dec_places),
                    token_symbol,
                    "minted" if is_mint else "redeemed",
                ),
                log_model=ev
            )
        )

    return events
