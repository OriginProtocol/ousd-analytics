from datetime import datetime
from eth_hash.auto import keccak
from eth_abi import decode_single
from eth_utils import encode_hex, decode_hex
from django.db.models import Q
from core.common import decode_calls
from core.addresses import CONTRACT_ADDR_TO_NAME
from notify.events import event_high


SIG_EVENT_PROPOSAL_CREATED = encode_hex(
    keccak(
        b"ProposalCreated(uint256,address,address[],string[],bytes[],string)"
    )
)
SIG_EVENT_PROPOSAL_QUEUED = encode_hex(
    keccak(b"ProposalQueued(uint256,uint256)")
)
SIG_EVENT_PROPOSAL_EXECUTED = encode_hex(keccak(b"ProposalExecuted(uint256)"))
SIG_EVENT_PROPOSAL_CANCELLED = encode_hex(
    keccak(b"ProposalCancelled(uint256)")
)
HUMAN_DATETIME_FORMAT = '%A, %B %e, %Y @ %H:%M UTC'


def get_proposal_events(logs):
    """ Get Mint/Redeem events """
    return logs.filter(
        Q(topic_0=SIG_EVENT_PROPOSAL_CREATED)
        | Q(topic_0=SIG_EVENT_PROPOSAL_QUEUED)
        | Q(topic_0=SIG_EVENT_PROPOSAL_EXECUTED)
        | Q(topic_0=SIG_EVENT_PROPOSAL_CANCELLED)
    ).order_by('block_number')


def run_trigger(new_logs):
    """ Create events for governor proposals """
    events = []

    for ev in get_proposal_events(new_logs):
        if ev.topic_0 == SIG_EVENT_PROPOSAL_CREATED:
            (
                proposal_id,
                proposer,
                targets,
                signatures,
                calldatas,
                description
            ) = decode_single(
                '(uint256,address,address[],string[],bytes[],string)',
                decode_hex(ev.data)
            )

            title = "New Proposal   🗳️"
            details = (
                "A new proposal ({}) was created: {}\n"
                "\n"
                "Proposer: {}\n"
                "Targets: {}\n"
                "Calls: \n - {}\n"
            ).format(
                proposal_id,
                description,
                proposer,
                ', '.join([
                    CONTRACT_ADDR_TO_NAME.get(target, target)
                    for target in set(targets)
                ]),
                '\n - '.join(decode_calls(signatures, calldatas)),
            )

        elif ev.topic_0 == SIG_EVENT_PROPOSAL_QUEUED:
            (proposal_id, eta_seconds) = decode_single(
                '(uint256,uint256)',
                decode_hex(ev.data)
            )
            eta = datetime.utcfromtimestamp(eta_seconds)

            title = "Proposal Queued   🗳️ ✔️"
            details = "Prop {} was accepted and queued for {}.".format(
                proposal_id,
                eta.strftime(HUMAN_DATETIME_FORMAT)
            )

        elif ev.topic_0 == SIG_EVENT_PROPOSAL_EXECUTED:
            (proposal_id,) = decode_single('(uint256)', decode_hex(ev.data))
            title = "Proposal Executed   🗳️ ⚙️"
            details = "Prop {} was executed.".format(proposal_id)

        elif ev.topic_0 == SIG_EVENT_PROPOSAL_CANCELLED:
            (proposal_id,) = decode_single('(uint256)', decode_hex(ev.data))
            title = "Proposal Cancelled   🗳️ ❌"
            details = "Prop {} was cancelled.".format(proposal_id)

        else:
            raise Exception("Impossible!")

        events.append(event_high(title, details))

    return events
