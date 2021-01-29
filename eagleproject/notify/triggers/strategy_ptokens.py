""" Strategy pToken changes

Events:
- PTokenAdded(address indexed _asset, address _pToken);
- PTokenRemoved(address indexed _asset, address _pToken);
"""
from django.db.models import Q
from eth_utils import decode_hex
from eth_abi import decode_single

from core.blockchain.addresses import CONTRACT_ADDR_TO_NAME
from core.blockchain.const import SYMBOL_FOR_CONTRACT
from core.blockchain.sigs import (
    SIG_EVENT_PTOKEN_ADDED,
    SIG_EVENT_PTOKEN_REMOVED,
)
from notify.events import event_normal, event_high


def get_events(logs):
    """ Get events """
    return logs.filter(
        Q(topic_0=SIG_EVENT_PTOKEN_ADDED)
        | Q(topic_0=SIG_EVENT_PTOKEN_REMOVED)
    ).order_by('block_number')


def run_trigger(new_logs):
    """ Template trigger """
    events = []

    for ev in get_events(new_logs):
        asset = decode_single('(address)', decode_hex(ev.topic_1))[0]
        ptoken = decode_single('(address)', decode_hex(ev.data))[0]

        asset_name = SYMBOL_FOR_CONTRACT.get(asset, asset)
        contract_name = CONTRACT_ADDR_TO_NAME.get(ev.address, ev.address)

        if ev.topic_0 == SIG_EVENT_PTOKEN_ADDED:
            events.append(
                event_normal(
                    "Platform token has been set   🪆",
                    "**Strategy**: {}\n"
                    "**Asset**: {}\n"
                    "**Platform Token**: {}\n".format(
                        contract_name,
                        asset_name,
                        ptoken,
                    ),
                    block_number=ev.block_number,
                    transaction_index=ev.transaction_index,
                    log_index=ev.log_index
                )
            )

        elif ev.topic_0 == SIG_EVENT_PTOKEN_REMOVED:
            events.append(
                event_high(
                    "Platform token has been unset   🕳️",
                    "**Strategy**: {}\n"
                    "**Asset**: {}\n"
                    "**Platform Token**: {}\n".format(
                        contract_name,
                        asset_name,
                        ptoken,
                    ),
                    block_number=ev.block_number,
                    transaction_index=ev.transaction_index,
                    log_index=ev.log_index
                )
            )

        else:
            # Theoretically impossible
            raise Exception('Unexpected event')

    return events
