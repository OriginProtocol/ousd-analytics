from eth_abi import decode_single
from eth_utils import decode_hex
from django.db.models import Q

from core.blockchain.const import SYMBOL_FOR_CONTRACT
from core.blockchain.sigs import (
    SIG_EVENT_DEFAULT_STRATEGY,
    SIG_EVENT_STRATEGY_APPROVED,
    SIG_EVENT_STRATEGY_ADDED,
    SIG_EVENT_STRATEGY_REMOVED,
    SIG_EVENT_WEIGHTS_UPDATED,
)
from notify.events import event_high

from core.blockchain.addresses import CONTRACT_ADDR_TO_NAME

def get_strategy_events(logs):
    """ Get strategy related events """
    return logs.filter(
        Q(topic_0=SIG_EVENT_DEFAULT_STRATEGY)
        | Q(topic_0=SIG_EVENT_STRATEGY_APPROVED)
        | Q(topic_0=SIG_EVENT_STRATEGY_ADDED)
        | Q(topic_0=SIG_EVENT_STRATEGY_REMOVED)
        | Q(topic_0=SIG_EVENT_WEIGHTS_UPDATED)
    ).order_by("block_number")


def run_trigger(new_logs):
    """ Look for mints and redeems """
    events = []

    for ev in get_strategy_events(new_logs):
        title = ""
        description = ""

        contract_name = CONTRACT_ADDR_TO_NAME.get(ev.address, ev.address)

        if ev.topic_0 == SIG_EVENT_DEFAULT_STRATEGY:
            title = "Asset Default Strategy Set   ♟️"
            asset, strat_addr = decode_single(
                "(address,address)", decode_hex(ev.data)
            )
            description = (
                "New default strategy for {} has been set to {} on {}"
            ).format(
                SYMBOL_FOR_CONTRACT.get(asset, asset),
                strat_addr,
                contract_name,
            )

        elif ev.topic_0 == SIG_EVENT_STRATEGY_APPROVED:
            title = "Strategy Approved On {}    🏦♟️".format(contract_name)
            strat_addr = decode_single("(address)", decode_hex(ev.data))[0]
            description = "New strategy {} has been approved on the {}".format(
                strat_addr,
                contract_name,
            )

        elif ev.topic_0 == SIG_EVENT_STRATEGY_ADDED:
            title = "Strategy Added to {}   ♘".format(contract_name)
            strat_addr = decode_single("(address)", decode_hex(ev.data))[0]
            description = "https://etherscan.io/address/{}".format(strat_addr)

        elif ev.topic_0 == SIG_EVENT_STRATEGY_REMOVED:
            title = "Strategy Removed from {}   ♞".format(contract_name)
            strat_addr = decode_single("(address)", decode_hex(ev.data))[0]
            description = "https://etherscan.io/address/{}".format(strat_addr)

        elif ev.topic_0 == SIG_EVENT_WEIGHTS_UPDATED:
            title = "Strategy Weights Updated on {}   ⚖️".format(contract_name)
            addresses, weights = decode_single(
                "(address[],uint256[])", decode_hex(ev.data)
            )
            for i, address in enumerate(addresses):
                description += "\n{} {}".format(address, weights[i])

        events.append(event_high(title, description, log_model=ev))

    return events
