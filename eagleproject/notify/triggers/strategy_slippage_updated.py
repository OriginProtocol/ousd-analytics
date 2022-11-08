from eth_utils import decode_hex
from eth_abi import decode_single

from core.blockchain.addresses import (
    CONTRACT_ADDR_TO_NAME,
)
from core.common import format_token_human
from core.blockchain.sigs import SIG_EVENT_MAX_SLIPPAGE_UPDATED
from notify.events import event_normal


def get_events(logs):
    """ Get events """
    return logs.filter(topic_0=SIG_EVENT_MAX_SLIPPAGE_UPDATED).order_by(
        "block_number"
    )


def run_trigger(new_logs):
    """ Template trigger """
    events = []

    for ev in get_events(new_logs):
        prev_slippage, new_slippage = decode_single(
            "(uint256,uint256)", decode_hex(ev.data)
        )

        contract_name = CONTRACT_ADDR_TO_NAME.get(ev.address, ev.address)

        events.append(
            event_normal(
                "Max Withdrawal Slippage Updated   💸",
                "From {} to {} on {} contract\n".format(
                    format_token_human("OUSD", prev_slippage),
                    format_token_human("OUSD", new_slippage),
                    contract_name,
                ),
                log_model=ev,
            )
        )

    return events
