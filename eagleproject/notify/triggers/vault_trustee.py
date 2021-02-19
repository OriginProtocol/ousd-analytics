from decimal import Decimal

from eth_abi import decode_single
from eth_utils import decode_hex
from django.db.models import Q

from core.blockchain.addresses import VAULT
from core.blockchain.sigs import (
    SIG_EVENT_YIELD_DISTRIBUTION,
    SIG_EVENT_TRUSTEE_ADDRESS_CHANGED,
    SIG_EVENT_TRUSTEE_FEE_CHANGED,
)
from core.common import format_token_human
from notify.events import event_low


def get_pause_events(logs):
    """ Get Vault trustee events events """
    return logs.filter(address=VAULT).filter(Q(
        Q(topic_0=SIG_EVENT_YIELD_DISTRIBUTION)
        | Q(topic_0=SIG_EVENT_TRUSTEE_ADDRESS_CHANGED)
        | Q(topic_0=SIG_EVENT_TRUSTEE_FEE_CHANGED)
    )).order_by('block_number')


def run_trigger(new_logs):
    """ Template trigger """
    events = []

    for ev in get_pause_events(new_logs):
        if ev.topic_0 == SIG_EVENT_YIELD_DISTRIBUTION:
            trustee, yield_amount, fee = decode_single(
                "(address,uint256,uint256)",
                decode_hex(ev.data)
            )

            events.append(
                event_low(
                    "Fee Distributed to Trustee Account   🕴️",
                    "**Yield**: {}\n"
                    "**Trustee**: {}\n"
                    "**Fee**: {}".format(
                        format_token_human('OUSD', Decimal(yield_amount)),
                        trustee,
                        format_token_human('OUSD', Decimal(fee)),
                    ),
                    log_model=ev
                )
            )

        elif ev.topic_0 == SIG_EVENT_TRUSTEE_ADDRESS_CHANGED:
            trustee = decode_single("(address)", decode_hex(ev.data))[0]

            events.append(
                event_low(
                    "Trustee Changed   🕴️➡️🕴️",
                    "**New Trustee**: {}".format(trustee),
                    log_model=ev
                )
            )

        elif ev.topic_0 == SIG_EVENT_TRUSTEE_FEE_CHANGED:
            bps = decode_single("(uint256)", decode_hex(ev.data))[0]

            events.append(
                event_low(
                    "Trustee Fee Changed   💲🕴️",
                    "**New Fee**: {}bps".format(bps),
                    log_model=ev
                )
            )

    return events
