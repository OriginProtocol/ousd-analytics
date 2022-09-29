""" Trigger for timelock transactions """
from datetime import datetime, timedelta
from django.db.models import Q
from eth_utils import decode_hex
from eth_abi import decode_single

from core.blockchain.addresses import (
    CONTRACT_ADDR_TO_NAME
)
from core.blockchain.sigs import (
    SIG_EVENT_CALL_SCHEDULED,
    SIG_EVENT_CALL_CANCELLED,
    SIG_EVENT_CALL_EXECUTED
)
from core.blockchain.addresses import GOVERNANCE_TIMELOCK
from notify.events import event_high


def get_events(logs):
    """ Get events """
    return logs.filter(address=GOVERNANCE_TIMELOCK).filter(
        Q(topic_0=SIG_EVENT_CALL_SCHEDULED)
        | Q(topic_0=SIG_EVENT_CALL_CANCELLED)
        | Q(topic_0=SIG_EVENT_CALL_EXECUTED)
    ).order_by('block_number')


def run_trigger(new_logs):
    """ OUSD Timelock calls """
    events = []

    for ev in get_events(new_logs):

        if ev.topic_0 == SIG_EVENT_CALL_SCHEDULED:
            # CallScheduled(
            #     bytes32 indexed id,
            #     uint256 indexed index,
            #     address target,
            #     uint256 value,
            #     bytes data,
            #     bytes32 predecessor,
            #     uint256 delay
            # );
            (
                id,
                index,
                target,
                value,
                data,
                predecessor,
                delay
            ) = decode_single(
                "(bytes32,uint256,address,uint256,bytes,bytes32,uint256)",
                decode_hex(ev.data)
            ) 
            delay = timedelta(seconds=delay)

            events.append(event_high(
                "OUSD Timelock transaction has been Queued\n\n"
                "**Target**: {}\n"
                "**Delay**: {} UTC\n"
                "**Index**: {}\n"
                "**Id**: {}\n"
                "**Data**: {}".format(
                    CONTRACT_ADDR_TO_NAME.get(target, target),
                    delay,
                    index,
                    id,
                    data
                ),
                log_model=ev
            ))

        elif ev.topic_0 == SIG_EVENT_CALL_EXECUTED:
            # event CallExecuted(bytes32 indexed id, uint256 indexed index, address target, uint256 value, bytes data);
            (
                id,
                index,
                target,
                value,
                data
            ) = decode_single(
                "(bytes32,uint256,address,uint256,bytes)",
                decode_hex(ev.data)
            ) 

            events.append(event_high(
                "OUSD Timelock transaction has been Executed\n\n"
                "**Target**: {}\n"
                "**Index**: {}\n"
                "**Id**: {}\n"
                "**Data**: {}".format(
                    CONTRACT_ADDR_TO_NAME.get(target, target),
                    index,
                    id,
                    data,
                ),
                log_model=ev
            ))

        elif ev.topic_0 == SIG_EVENT_CALL_CANCELLED:
            # event Cancelled(bytes32 indexed id);
            id = decode_single(
                "(bytes32)",
                decode_hex(ev.data)[0]
            )

            events.append(event_high(
                "OUSD Timelock transaction has been Cancelled\n\n"
                "**Id**: {}\n".format(
                    id
                ),
                log_model=ev
            ))

    return events
