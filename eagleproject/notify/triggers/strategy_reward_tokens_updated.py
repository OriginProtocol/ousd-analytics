from eth_utils import decode_hex
from eth_abi import decode_single

from core.blockchain.addresses import (
    CONTRACT_ADDR_TO_NAME,
)
from core.common import format_token_human
from core.blockchain.sigs import SIG_EVENT_REWARD_TOKENS_UPDATED
from notify.events import event_normal


def get_events(logs):
    """ Get events """
    return logs.filter(topic_0=SIG_EVENT_REWARD_TOKENS_UPDATED).order_by(
        "block_number"
    )


def run_trigger(new_logs):
    """ Template trigger """
    events = []

    for ev in get_events(new_logs):
        prev_reward_tokens, new_reward_tokens = decode_single(
            "(address[],address[])", decode_hex(ev.data)
        )

        contract_name = CONTRACT_ADDR_TO_NAME.get(ev.address, ev.address)

        desc = "New reward tokens for {} contract:\n".format(contract_name)

        for token_addr in new_reward_tokens:
            desc += " - {}".format(token_addr)

        events.append(
            event_normal(
                "Reward Tokens Updated   💸",
                desc,
                log_model=ev,
            )
        )

    return events
