from decimal import Decimal
from eth_abi import decode_single
from eth_utils import decode_hex
from django.db.models import Q, Sum
from core.common import format_ousd_human, format_token_human
from core.models import StoryStake
from core.blockchain.addresses import (
    CONTRACT_ADDR_TO_NAME,
    OGN,
    STORY_STAKING_SEASONS,
    STORY_STAKING_SERIES,
    STORY_STAKING_VAULT,
)
from core.blockchain.const import E_18
from core.blockchain.sigs import (
    SIG_EVENT_ERC20_TRANSFER,
    SIG_EVENT_STAKE,
    SIG_EVENT_UNSTAKE,
)
from core.logging import get_logger
from notify.events import event_normal

log = get_logger(__name__)

EVENT_TAGS = ["ogn"]


def get_stake_unstake_events(logs):
    """ Get Stake/Unstake events """
    return logs.filter(
        Q(address__in=STORY_STAKING_SEASONS)
        & Q(Q(topic_0=SIG_EVENT_STAKE) | Q(topic_0=SIG_EVENT_UNSTAKE))
    ).order_by("block_number")


def get_ogn_unstake_transfer_event(logs, tx_hash):
    """ Get OGN transfer indicating an unstake """
    evs = logs.filter(
        address=OGN,
        transaction_hash=tx_hash,
        topic_0=SIG_EVENT_ERC20_TRANSFER,
    ).order_by("log_index")

    ogn_unstake_ev = None

    for ev in evs:
        from_address = decode_single("(address)", decode_hex(ev.topic_1))[0]

        if from_address == STORY_STAKING_SERIES:
            ogn_unstake_ev = ev

    return ogn_unstake_ev


def run_trigger(new_logs):
    """Look for Stake/Withdraw

    Stake(address indexed userAddress, uint256 indexed amount, uint256 points)
    Unstake(address indexed userAddress)
    """
    events = []

    for ev in get_stake_unstake_events(new_logs):
        if ev.topic_0 == SIG_EVENT_STAKE:
            user_address = decode_single("(address)", decode_hex(ev.topic_1))[0]
            amount = decode_single("(uint256)", decode_hex(ev.topic_2))[0]
            points = decode_single("(uint256)", decode_hex(ev.data))[0]

            events.append(
                event_normal(
                    "{} Stake    🥩".format(
                        CONTRACT_ADDR_TO_NAME.get(ev.address, "")
                    ),
                    "{} staked {} OGN for a total of {} points".format(
                        user_address[:6],
                        format_ousd_human(Decimal(amount) / Decimal(1e18)),
                        format_ousd_human(points / E_18),
                    ),
                    tags=EVENT_TAGS,
                    log_model=ev,
                )
            )
        elif ev.topic_0 == SIG_EVENT_UNSTAKE:
            ogn_unstake_ev = get_ogn_unstake_transfer_event(
                new_logs, ev.transaction_hash
            )
            user_address = decode_single("(address)", decode_hex(ev.topic_1))[0]

            # If there's no transfer of OGN from series to user, it's not an
            # unstake from the Series, just a claim
            if ogn_unstake_ev:
                res = StoryStake.objects.filter(
                    user_address=user_address, unstake_block=ev.block_number
                ).aggregate(stake_total=Sum("amount"))

                if res["stake_total"] is None:
                    log.error(
                        f"Unstake was not recorded for transaction {ev.transaction_hash}"
                    )
                    continue

                unstake_amount = format_token_human("OGN", res["stake_total"])

                events.append(
                    event_normal(
                        "{} Unstake   💔".format(
                            CONTRACT_ADDR_TO_NAME.get(ev.address, "")
                        ),
                        f"{user_address[:6]} unstaked {unstake_amount} OGN",
                        tags=EVENT_TAGS,
                        log_model=ev,
                    )
                )

    return events
