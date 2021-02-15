from datetime import timedelta
from django.db.models import Q
from eth_utils import decode_hex
from eth_abi import decode_single

from core.blockchain.addresses import (
    CURVE_ARAGON_51,
    CURVE_ARAGON_60,
    CONTRACT_ADDR_TO_NAME,
)
from core.blockchain.sigs import (
    SIG_EVENT_START_VOTE,
    SIG_EVENT_EXECUTE_VOTE,
    SIG_EVENT_SCRIPT_RESULT,
)
from core.common import format_token_human, format_timedelta
from core.ipfs import strip_terrible_ipfs_prefix, fetch_ipfs_json
from notify.events import event_high, event_normal


def get_events(logs):
    """ Get Aragon voting events """
    return logs.filter(
        Q(address=CURVE_ARAGON_51)
        | Q(address=CURVE_ARAGON_60)
    ).filter(
        Q(topic_0=SIG_EVENT_START_VOTE)
        | Q(topic_0=SIG_EVENT_EXECUTE_VOTE)
        | Q(topic_0=SIG_EVENT_SCRIPT_RESULT)
    ).order_by('block_number')


def run_trigger(new_logs):
    """ Template trigger """
    events = []

    for ev in get_events(new_logs):

        if ev.topic_0 == SIG_EVENT_START_VOTE:
            # StartVote(
            #     uint256 indexed voteId,
            #     address indexed creator,
            #     string metadata,
            #     uint256 minBalance,
            #     uint256 minTime,
            #     uint256 totalSupply,
            #     uint256 creatorVotingPower
            # )
            vote_id = decode_single('(uint256)', decode_hex(ev.topic_1))[0]
            creator = decode_single('(address)', decode_hex(ev.topic_2))[0]
            (
                metadata_hash,
                min_balance,
                min_time,
                total_supply,
                creator_voting_power,
            ) = decode_single(
                "(string,uint256,uint256,uint256,uint256)",
                decode_hex(ev.data)
            )

            metadata = fetch_ipfs_json(
                strip_terrible_ipfs_prefix(metadata_hash)
            )

            details = (
                "**Creator**: {} \n"
                "**Creator Voting Power**: {} veCRV\n"
                "**Minimum vote balance**: {} veCRV\n"
                "**Current total supply**: {} veCRV\n"
                "**Minimum time**: {}\n"
                "**Metadata**: {}\n"
            ).format(
                creator,
                format_token_human('veCRV', creator_voting_power),
                format_token_human('veCRV', min_balance),
                format_token_human('veCRV', total_supply),
                format_timedelta(timedelta(seconds=min_time)),
                metadata.get('text', 'NO METADATA TEXT FOUND.'),
            )

            events.append(event_high(
                "{} - Vote Created ({})   🗳️ 🆕".format(
                    CONTRACT_ADDR_TO_NAME.get(ev.address, ev.address),
                    vote_id,
                ),
                details,
                log_model=ev
            ))

        elif ev.topic_0 == SIG_EVENT_EXECUTE_VOTE:
            # ExecuteVote(uint256 indexed voteId)
            vote_id = decode_single('(uint256)', decode_hex(ev.topic_1))[0]

            events.append(event_high(
                "{} - Vote Executed ({})   🗳️ ⚙️".format(
                    CONTRACT_ADDR_TO_NAME.get(ev.address, ev.address),
                    vote_id,
                ),
                "Curve Aragon DAO vote #{} on the {} voting app has been "
                "executed".format(
                    vote_id,
                    CONTRACT_ADDR_TO_NAME.get(
                        ev.address,
                        ev.address
                    ),
                ),
                log_model=ev
            ))

        elif ev.topic_0 == SIG_EVENT_SCRIPT_RESULT:
            # ScriptResult(
            #     address indexed executor,
            #     bytes script,
            #     bytes input,
            #     bytes returnData
            # )
            executor = decode_single('(address)', decode_hex(ev.topic_1))[0]
            # script, input_data, return_data = decode_single(
            #     "(bytes,bytes,bytes)",
            #     decode_hex(ev.data),
            # )

            """ TODO: Decode this further?  Right now I don't think it's worth
            the effort, though we're putting a bit of trust into the prop that
            it's nothing nefarious.  Might be worth coming back to this.  Only
            problem is that it appears to be EVM-level instructions...

            Ref: https://hack.aragon.org/docs/evmscript_EVMScriptRunner
            Ref: https://github.com/aragon/aragonOS/blob/f3ae59b00f73984e562df00129c925339cd069ff/contracts/evmscript/EVMScriptRunner.sol#L34-L100
            """
            # print('script', script)
            # print('input_data:', input_data)
            # print('return_data:', return_data)

            events.append(event_normal(
                "{} - Execution Result   🗳️ 🪣".format(
                    CONTRACT_ADDR_TO_NAME.get(ev.address, ev.address)
                ),
                "Executed by: {}".format(executor),
                log_model=ev
            ))

    return events
