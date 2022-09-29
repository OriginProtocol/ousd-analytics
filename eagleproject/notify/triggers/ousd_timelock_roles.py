""" Trigger for timelock role changes """
from django.db.models import Q
from eth_utils import decode_hex
from eth_abi import decode_single

from core.blockchain.addresses import GOVERNANCE_TIMELOCK
from core.blockchain.sigs import (
    SIG_EVENT_ROLE_ADMIN_CHANGED, 
    SIG_EVENT_ROLE_GRANTED,
    SIG_EVENT_ROLE_REVOKED
)
from notify.events import event_high


def get_events(logs):
    """ Get Role changed events """
    return logs.filter(address=GOVERNANCE_TIMELOCK).filter(
        Q(topic_0=SIG_EVENT_ROLE_ADMIN_CHANGED)
        | Q(topic_0=SIG_EVENT_ROLE_GRANTED)
        | Q(topic_0=SIG_EVENT_ROLE_REVOKED)
    ).order_by('block_number')


def run_trigger(new_logs):
    """ OUSD Role changes """
    events = []

    for ev in get_events(new_logs):

        if ev.topic_0 == SIG_EVENT_ROLE_ADMIN_CHANGED:
           # event RoleAdminChanged(bytes32 indexed role, bytes32 indexed previousAdminRole, bytes32 indexed newAdminRole);
            (
                role,
                previousAdminRole,
                newAdminRole
            ) = decode_single(
                "(bytes32,bytes32,bytes32)",
                decode_hex(ev.data)
            ) 

            events.append(event_high(
                "OUSD Timelock admin role has been Changed\n\n"
                "**Role**: {}\n"
                "**Previous Admin Role**: {} UTC\n"
                "**New Admin Role**: {}\n".format(
                    role,
                    previousAdminRole,
                    newAdminRole
                ),
                log_model=ev
            ))

        elif ev.topic_0 == SIG_EVENT_ROLE_GRANTED or ev.topic_0 == SIG_EVENT_ROLE_REVOKED:
            # RoleGranted(bytes32 indexed role, address indexed account, address indexed sender);
            # RoleRevoked(bytes32 indexed role, address indexed account, address indexed sender);
            # Signature is the same so we can reuse code
            role_status = 'granted'
            if ev.topic_0 == SIG_EVENT_ROLE_REVOKED:
                role_status = 'revoked'

            (
                role,
                account,
                sender
            ) = decode_single(
                "(bytes32,address, address)",
                decode_hex(ev.data)
            )

            events.append(event_high(
                "OUSD Timelock role has been {}\n\n"
                "**Role**: {}\n"
                "**Account**: {}\n"
                "**Sender**: {}\n".format(
                    role_status,
                    role,
                    account,
                    sender
                ),
                log_model=ev
            ))

    return events
