from eth_abi import decode_single
from eth_utils import decode_hex

from core.blockchain.addresses import STORY_STAKING_VAULT
from core.blockchain.const import SYMBOL_FOR_CONTRACT
from core.blockchain.sigs import SIG_EVENT_REWARDS_SENT
from core.common import format_ousd_human

from notify.events import event_low

EVENT_TAGS = ["ogn"]


def get_rewards_events(logs):
    """ Get RewardsSent events """
    return logs.filter(
        address=STORY_STAKING_VAULT, topic_0=SIG_EVENT_REWARDS_SENT
    ).order_by("block_number")


def run_trigger(new_logs):
    """ Template trigger """
    events = []

    for ev in get_rewards_events(new_logs):
        asset = decode_single("(address)", decode_hex(ev.topic_1))[0]
        to_address = decode_single("(address)", decode_hex(ev.topic_2))[0]
        amount = format_ousd_human(
            decode_single("(uint256)", decode_hex(ev.data))[0]
        )

        symbol = SYMBOL_FOR_CONTRACT[asset]

        events.append(
            event_low(
                "Rewards Sent   💸",
                f"{amount} {symbol} paid to {to_address}",
                tags=EVENT_TAGS,
                log_model=ev,
            )
        )

    return events
