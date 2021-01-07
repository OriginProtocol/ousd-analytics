from eth_abi import decode_single
from eth_utils import decode_hex
from django.db.models import Q

from core.sigs import (
    SIG_EVENT_STRATEGY_ADDED,
    SIG_EVENT_STRATEGY_REMOVED,
    SIG_EVENT_WEIGHTS_UPDATED,
)
from notify.events import event_high


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
