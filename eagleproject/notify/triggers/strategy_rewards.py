""" Strategy pToken changes

Events:
- RewardTokenCollected(address recipient, uint256 amount)
"""
from eth_utils import decode_hex
from eth_abi import decode_single

from core.blockchain.addresses import STRATCOMP, CONTRACT_ADDR_TO_NAME
from core.common import format_token_human
from core.blockchain.sigs import SIG_EVENT_REWARDS_COLLECTED
from notify.events import event_normal


def get_events(logs):
    """ Get events """
    return logs.filter(
        topic_0=SIG_EVENT_REWARDS_COLLECTED
    ).order_by('block_number')


def run_trigger(new_logs):
    """ Template trigger """
    events = []

    for ev in get_events(new_logs):
        recipient, amount = decode_single(
            '(address,uint256)',
            decode_hex(ev.data)
        )

        if amount == 0:
            continue

        contract_name = CONTRACT_ADDR_TO_NAME.get(ev.address, ev.address)

        """ Event doesn't include token address, so if it's not from STRATCOMP,
        I have no idea what it might be.
        """
        reward_token = '[UKNOWN]'
        if ev.address == STRATCOMP:
            reward_token = 'COMP'

        events.append(
            event_normal(
                "Reward tokens have been collected   💸",
                "{} {} has been collected by {}\n".format(
                    format_token_human('COMP', amount),
                    reward_token,
                    contract_name,
                )
            )
        )

    return events
