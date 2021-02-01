""" Trigger for timelock admin changes """
import re
import requests
from decimal import Decimal
from django.db.models import Q
from eth_utils import decode_hex, encode_hex
from eth_abi import decode_single

from core.blockchain.addresses import AAVE_PROTO_GOVERNANCE_V1
from core.blockchain.const import BLOCKS_PER_DAY
from core.blockchain.sigs import (
    SIG_EVENT_AAVE_PROPOSAL_CREATED,
    SIG_EVENT_STATUS_CHANGE_TO_VOTING,
    SIG_EVENT_STATUS_CHANGE_TO_VALIDATING,
    SIG_EVENT_STATUS_CHANGE_TO_EXECUTED,
    SIG_EVENT_WINS_YES,
    SIG_EVENT_WINS_NO,
    SIG_EVENT_WINS_ABSTAIN,
)
from core.common import format_token_human, decode_ipfs_hash
from core.logging import get_logger
from notify.events import event_high, event_normal

log = get_logger(__name__)

HEADER_PATTERN = r'^([\w\d_]+): (.+)'


def fetch_ipfs_json(ipfs_hash):
    """ Fetch a JSON IPFS object """
    if not ipfs_hash:
        return {}

    r = requests.get('https://ipfs.io/ipfs/{}'.format(ipfs_hash))

    if r.status_code != 200:
        log.error('Failed to fetch file from IPFS: {}'.format(ipfs_hash))
        return {}

    return r.json()


def parse_prop_headers(prop_json):
    description = prop_json.get('description')

    if not description:
        return {}

    headers = {}
    in_header_block = False

    for ln in description.split('\n'):
        if ln.startswith('---'):
            if in_header_block:
                break

            in_header_block = True

            continue

        match = re.match(HEADER_PATTERN, ln)

        if not match:
            break

        groups = match.groups()
        headers[groups[0]] = groups[1]

    return headers


def get_events(logs):
    """ Get Mint/Redeem events """
    return logs.filter(address=AAVE_PROTO_GOVERNANCE_V1).filter(
        Q(topic_0=SIG_EVENT_AAVE_PROPOSAL_CREATED)
        | Q(topic_0=SIG_EVENT_STATUS_CHANGE_TO_VALIDATING)
        | Q(topic_0=SIG_EVENT_STATUS_CHANGE_TO_VOTING)
        | Q(topic_0=SIG_EVENT_STATUS_CHANGE_TO_EXECUTED)
        | Q(topic_0=SIG_EVENT_WINS_YES)
        | Q(topic_0=SIG_EVENT_WINS_NO)
        | Q(topic_0=SIG_EVENT_WINS_ABSTAIN)
    )


def run_trigger(new_logs):
    """ Compound Timelock changes """
    events = []

    for ev in get_events(new_logs):
        if ev.topic_0 == SIG_EVENT_AAVE_PROPOSAL_CREATED:
            """
            event ProposalCreated(
                uint256 indexed proposalId,
                bytes32 indexed ipfsHash,
                bytes32 indexed proposalType,
                uint256 propositionPowerOfCreator,
                uint256 threshold,
                uint256 maxMovesToVotingAllowed,
                uint256 votingBlocksDuration,
                uint256 validatingBlocksDuration,
                address proposalExecutor
            )
            """
            proposal_id = decode_single("(uint256)", decode_hex(ev.topic_1))[0]
            ipfs_hash = decode_single("(bytes32)", decode_hex(ev.topic_2))[0]
            # proposal_type = decode_single(
            #     "(bytes32)",
            #     decode_hex(ev.topic_3)
            # )[0]
            (
                proposition_power_of_creator,
                threshold,
                max_moves_to_voting_allowed,
                voting_blocks_duration,
                validating_blocks_duration,
                proposal_executor,
            ) = decode_single(
                "(uint256,uint256,uint256,uint256,uint256,address)",
                decode_hex(ev.data)
            )

            b58_ipfs_data = decode_ipfs_hash(encode_hex(ipfs_hash))
            ipfs_data = fetch_ipfs_json(b58_ipfs_data)
            prop_headers = parse_prop_headers(ipfs_data)
            aip = prop_headers.get('aip')

            if aip:
                aip_link = 'https://aave.github.io/aip/AIP-{}'.format(aip)
            else:
                aip_link = '[UNKNOWN AIP]'

            events.append(event_high(
                "Aave (v1) Governance Proposal Created (ID: {})   🗳️ 🆕".format(
                    proposal_id
                ),
                "A new proposal (ID: {}) has been submitted for Aave"
                "\n\n"
                "**Title**: {}\n"
                "**Description**: {}\n\n"
                "**Threshold**: {} AAVE\n"
                "**Voting Duration** {} blocks (approx {} days)\n"
                "**Validating Duration** {} blocks (approx {} days)\n"
                "**Executor**: {}\n"
                "**IPFS Hash**: {}\n"
                "{}".format(
                    proposal_id,
                    ipfs_data.get('title'),
                    ipfs_data.get('shortDescription'),
                    format_token_human('AAVE', Decimal(threshold)),
                    voting_blocks_duration,
                    round(
                        Decimal(voting_blocks_duration) / BLOCKS_PER_DAY,
                        2
                    ),
                    validating_blocks_duration,
                    round(
                        Decimal(validating_blocks_duration) / BLOCKS_PER_DAY,
                        2
                    ),
                    proposal_executor,
                    decode_ipfs_hash(encode_hex(ipfs_hash)),
                    aip_link,
                ),
                log_model=ev
            ))

        elif ev.topic_0 == SIG_EVENT_STATUS_CHANGE_TO_VALIDATING:
            # StatusChangeToValidating(uint256 indexed proposalId)
            proposal_id = decode_single("(uint256)", decode_hex(ev.topic_1))[0]

            events.append(event_high(
                "Aave proposal moved to validating   🗳️ 🔍",
                "Aave proposal #{} is now in validating stage awaiting "
                "challenges".format(
                    proposal_id
                ),
                log_model=ev
            ))

        elif ev.topic_0 == SIG_EVENT_STATUS_CHANGE_TO_VOTING:
            """
            StatusChangeToVoting(
                uint256 indexed proposalId,
                uint256 movesToVoting
            )
            """
            proposal_id = decode_single("(uint256)", decode_hex(ev.topic_1))[0]

            events.append(event_high(
                "Aave proposal moved to voting   🗳️ 📥",
                "Aave proposal #{} is now in voting stage".format(
                    proposal_id
                ),
                log_model=ev
            ))

        elif ev.topic_0 == SIG_EVENT_STATUS_CHANGE_TO_EXECUTED:
            """ StatusChangeToExecuted(uint256 indexed proposalId) """
            proposal_id = decode_single("(uint256)", decode_hex(ev.topic_1))[0]

            events.append(event_normal(
                "Aave proposal has been resolved   🗳️ ⚙️",
                "Aave proposal #{} has now been resolved".format(
                    proposal_id
                ),
                log_model=ev
            ))

        elif ev.topic_0 == SIG_EVENT_WINS_YES:
            """
            YesWins(
                uint256 indexed proposalId,
                uint256 abstainVotingPower,
                uint256 yesVotingPower,
                uint256 noVotingPower
            )
            """
            proposal_id = decode_single(
                "(uint256)",
                decode_hex(ev.topic_1)
            )[0]

            events.append(event_high(
                "Aave proposal has been passed   🗳️ ✅",
                "Aave proposal #{} has been passed".format(
                    proposal_id
                ),
                log_model=ev
            ))

        elif ev.topic_0 == SIG_EVENT_WINS_NO:
            """
            NoWins(
                uint256 indexed proposalId,
                uint256 abstainVotingPower,
                uint256 yesVotingPower,
                uint256 noVotingPower
            )
            """
            proposal_id = decode_single(
                "(uint256)",
                decode_hex(ev.topic_1)
            )[0]

            events.append(event_high(
                "Aave proposal has failed   🗳️ ❎",
                "Aave proposal #{} has been rejected".format(
                    proposal_id
                ),
                log_model=ev
            ))

        elif ev.topic_0 == SIG_EVENT_WINS_ABSTAIN:
            """
            AbstainWins(
                uint256 indexed proposalId,
                uint256 abstainVotingPower,
                uint256 yesVotingPower,
                uint256 noVotingPower
            )
            """
            proposal_id = decode_single(
                "(uint256)",
                decode_hex(ev.topic_1)
            )[0]

            events.append(event_high(
                "Aave proposal has failed by abstention   🗳️ 〰️",
                "Aave proposal #{} has been rejected by abstention".format(
                    proposal_id
                ),
                log_model=ev
            ))

    return events
