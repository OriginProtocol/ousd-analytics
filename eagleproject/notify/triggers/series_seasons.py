from eth_abi import decode_single
from eth_utils import decode_hex

from core.blockchain.addresses import STORY_STAKING_SERIES
from core.blockchain.sigs import (
    SIG_EVENT_FINALE,
    SIG_EVENT_NEW_SEASON,
    SIG_EVENT_SEASON_START,
    SIG_EVENT_SEASON_CANCELLED,
)
from core.common import format_ousd_human

from notify.events import event_high, event_normal

EVENT_TAGS = ["ogn"]


def get_rewards_events(logs):
    """ Get Series' Season events """
    return logs.filter(
        address=STORY_STAKING_SERIES,
        topic_0__in=[
            SIG_EVENT_NEW_SEASON,
            SIG_EVENT_SEASON_START,
            SIG_EVENT_SEASON_CANCELLED,
        ],
    ).order_by("block_number")


def run_trigger(new_logs):
    """ Create events for season changes """
    events = []

    for ev in get_rewards_events(new_logs):
        if ev.topic_0 == SIG_EVENT_NEW_SEASON:
            index = decode_single("(uint256)", decode_hex(ev.topic_1))[0]
            season_address = decode_single("(address)", decode_hex(ev.topic_2))[
                0
            ]

            events.append(
                event_normal(
                    "New Season   📅",
                    f"Season {index + 1} has been added to the series\n\n"
                    f"Address: {season_address}",
                    tags=EVENT_TAGS,
                    log_model=ev,
                )
            )

        elif ev.topic_0 == SIG_EVENT_SEASON_START:
            index = decode_single("(uint256)", decode_hex(ev.topic_1))[0]
            season_address = decode_single("(address)", decode_hex(ev.topic_2))[
                0
            ]

            events.append(
                event_normal(
                    "Season Started   🎬",
                    f"Season {index + 1} has begun!\n\nAddress: {season_address}",
                    tags=EVENT_TAGS,
                    log_model=ev,
                )
            )

        elif ev.topic_0 == SIG_EVENT_SEASON_CANCELLED:
            index = decode_single("(uint256)", decode_hex(ev.topic_1))[0]
            season_address = decode_single("(address)", decode_hex(ev.topic_2))[
                0
            ]

            events.append(
                event_high(
                    "Season Cancelled   🪓",
                    f"Season {index + 1} ({season_address}) has been "
                    "cancelled!  It will likely be replaced, stay tuned.",
                    tags=EVENT_TAGS,
                    log_model=ev,
                )
            )

        elif ev.topic_0 == SIG_EVENT_FINALE:
            rewards_eth, rewards_ogn = decode_single(
                "(uint256, uint256)", decode_hex(ev.data)
            )

            events.append(
                event_normal(
                    "Season Ended   🏁",
                    f"Season {index + 1} ({season_address}) has ended!\n\n"
                    "Rewards\n"
                    "-------\n"
                    f"- {format_ousd_human(rewards_eth)} ETH\n"
                    f"- {format_ousd_human(rewards_ogn)} OGN\n",
                    tags=EVENT_TAGS,
                    log_model=ev,
                )
            )

    return events
