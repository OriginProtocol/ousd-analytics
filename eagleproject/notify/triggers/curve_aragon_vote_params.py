from decimal import Decimal
from datetime import timedelta
from django.db.models import Q
from eth_utils import decode_hex
from eth_abi import decode_single

from core.blockchain.addresses import (
    CURVE_ARAGON_51,
    CURVE_ARAGON_60,
    CONTRACT_ADDR_TO_NAME,
)
from core.blockchain.const import E_18
from core.blockchain.sigs import (
    SIG_EVENT_CHANGE_SUPPORT_REQUIRED,
    SIG_EVENT_CHANGE_MIN_QUORUM,
    SIG_EVENT_MIN_BALANCE_SET,
    SIG_EVENT_MIN_TIME_SET,
    # Following 2 events deal with funds accidentally sent to contract.  meh
    # SIG_EVENT_RECOVER_TO_VAULT,
    # SIG_EVENT_CLAIMED_TOKENS,
    # Creates clone of the MiniMeToken (not currently used in Voting contract)
    # SIG_EVENT_NEW_CLONE_TOKEN,
    SIG_EVENT_SET_APP,
)
from core.common import format_token_human, format_timedelta
from notify.events import event_high, event_normal


def get_events(logs):
    """ Get Aragon Voting parameter change events """
    return logs.filter(
        Q(address=CURVE_ARAGON_51)
        | Q(address=CURVE_ARAGON_60)
    ).filter(
        Q(topic_0=SIG_EVENT_CHANGE_SUPPORT_REQUIRED)
        | Q(topic_0=SIG_EVENT_CHANGE_MIN_QUORUM)
        | Q(topic_0=SIG_EVENT_MIN_BALANCE_SET)
        | Q(topic_0=SIG_EVENT_MIN_TIME_SET)
        | Q(topic_0=SIG_EVENT_SET_APP)
    ).order_by('block_number')


def run_trigger(new_logs):
    """ Template trigger """
    events = []

    for ev in get_events(new_logs):

        if ev.topic_0 == SIG_EVENT_CHANGE_SUPPORT_REQUIRED:
            # ChangeSupportRequired(uint64 supportRequiredPct)
            support_required = decode_single(
                '(uint64)',
                decode_hex(ev.data)
            )[0]

            events.append(event_high(
                "{} - Support Required Changed   🎚️".format(
                    CONTRACT_ADDR_TO_NAME.get(ev.address, ev.address)
                ),
                "{}% support is now required for a vote pass. \n\n"
                "NOTE: This is unexpected due to two contracts for different "
                "voting levels.".format(Decimal(support_required) / E_18),
                log_model=ev
            ))

        elif ev.topic_0 == SIG_EVENT_CHANGE_MIN_QUORUM:
            # ChangeMinQuorum(uint64 minAcceptQuorumPct)
            min_quorum = decode_single(
                '(uint64)',
                decode_hex(ev.data)
            )[0]

            events.append(event_normal(
                "{} - Support Minimum Quorum   🎚️".format(
                    CONTRACT_ADDR_TO_NAME.get(ev.address, ev.address)
                ),
                "{}% quorum (yeas out of total supply) is now required for a vote.".format(
                    Decimal(min_quorum) / E_18
                ),
                log_model=ev
            ))

        elif ev.topic_0 == SIG_EVENT_MIN_BALANCE_SET:
            # MinimumBalanceSet(uint256 minBalance)
            min_balance = decode_single(
                '(uint256)',
                decode_hex(ev.data)
            )[0]

            events.append(event_normal(
                "{} - Minimum Balance   🎚️".format(
                    CONTRACT_ADDR_TO_NAME.get(ev.address, ev.address)
                ),
                "Minimum balance of {} is now required to create a governance "
                "vote.".format(
                    format_token_human('veCRV', min_balance)
                ),
                log_model=ev
            ))

        elif ev.topic_0 == SIG_EVENT_MIN_TIME_SET:
            # MinimumTimeSet(uint256 minTime)
            min_time = decode_single(
                '(uint256)',
                decode_hex(ev.data)
            )[0]

            events.append(event_normal(
                "{} - Minimum Time   🕓".format(
                    CONTRACT_ADDR_TO_NAME.get(ev.address, ev.address)
                ),
                "Governance vote creation rate limit has been changed to "
                "{}.".format(
                    format_timedelta(timedelta(seconds=min_time))
                ),
                log_model=ev
            ))

        elif ev.topic_0 == SIG_EVENT_SET_APP:
            # SetApp(bytes32 indexed namespace, bytes32 indexed appId, address app)
            namespace = decode_single(
                '(bytes32)',
                decode_hex(ev.topic_1)
            )[0]
            app_id = decode_single(
                '(bytes32)',
                decode_hex(ev.topic_1)
            )[0]
            app_address = decode_single(
                '(address)',
                decode_hex(ev.data)
            )[0]

            events.append(event_high(
                "{} - New App Set   📛".format(
                    CONTRACT_ADDR_TO_NAME.get(ev.address, ev.address)
                ),
                "A new Aragon app has been set for the Curve Voting Fork. "
                "This is expected to only happen on app creation.\n\n"
                "Namespace: {}\n"
                "App ID: {}\n"
                "App Address: {}\n".format(
                    namespace,
                    app_id,
                    app_address,
                ),
                log_model=ev
            ))

    return events
