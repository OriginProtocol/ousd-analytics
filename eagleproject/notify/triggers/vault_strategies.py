from eth_hash.auto import keccak
from eth_abi import decode_single
from eth_utils import encode_hex, decode_hex
from django.db.models import Q
from notify.events import event_high

SIG_EVENT_STRATEGY_ADDED = encode_hex(keccak(b"StrategyAdded(address)"))
SIG_EVENT_STRATEGY_REMOVED = encode_hex(keccak(b"StrategyRemoved(address)"))
SIG_EVENT_WEIGHTS_UPDATED = encode_hex(keccak(b"StrategyWeightsUpdated(address[],uint256[])"))


def get_strategy_events(logs):
    """ Get strategy related events """
    return logs.filter(
        Q(topic_0=SIG_EVENT_STRATEGY_ADDED)
        | Q(topic_0=SIG_EVENT_STRATEGY_REMOVED)
        | Q(topic_0=SIG_EVENT_WEIGHTS_UPDATED)
    ).order_by('block_number')


def run_trigger(new_logs):
    """ Look for mints and redeems """
    events = []

    for ev in get_strategy_events(new_logs):
        title = ''
        description = ''

        if ev.topic_0 == SIG_EVENT_STRATEGY_ADDED:
            title = 'Strategy Added   ♘'
            strat_addr = decode_single('(address)', decode_hex(ev.data))
            description = 'https://etherscan.io/address/{}'.format(strat_addr)

        elif ev.topic_0 == SIG_EVENT_STRATEGY_REMOVED:
            title = 'Strategy Removed   ♞'
            strat_addr = decode_single('(address)', decode_hex(ev.data))
            description = 'https://etherscan.io/address/{}'.format(strat_addr)

        elif ev.topic_0 == SIG_EVENT_WEIGHTS_UPDATED:
            title = 'Strategy Weights Updated   ⚖️'
            addresses, weights = decode_single(
                '(address[],uint256[])',
                decode_hex(ev.data)
            )
            for i, address in enumerate(addresses):
                description += '\n{} {}'.format(address, weights[i])

        events.append(event_high(title, description))

    return events
