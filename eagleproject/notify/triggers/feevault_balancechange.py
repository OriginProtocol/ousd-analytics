from eth_abi import decode_single
from eth_utils import decode_hex

from core.blockchain.addresses import STORY_STAKING_VAULT
from core.blockchain.const import SYMBOL_FOR_CONTRACT
from core.blockchain.sigs import SIG_EVENT_REWARDS_SENT
from core.common import format_ousd_human

from notify.events import event_critical, event_low

EVENT_TAGS = ["ogn"]


def get_rewards_events(logs):
    """ Get RewardsSent events """
    return logs.filter(
        address=STORY_STAKING_VAULT, topic_0=SIG_EVENT_REWARDS_SENT
    ).order_by("block_number")


def calculate_paid(events):
    paid = {}

    for ev in events:
        asset = decode_single("(address)", decode_hex(ev.topic_1))[0]
        amount = decode_single("(uint256)", decode_hex(ev.topic_3))[0]
        symbol = SYMBOL_FOR_CONTRACT[asset]

        if asset in SYMBOL_FOR_CONTRACT:
            if symbol not in paid:
                paid[symbol] = amount
            else:
                paid[symbol] += amount

    return paid


def run_trigger(new_logs, latest_story_snapshots):
    """ Template trigger """
    events = []
    snapshots = latest_story_snapshots(2)

    # Nothing to compare
    if len(snapshots) < 2:
        return

    paid = calculate_paid(get_rewards_events(new_logs))
    paid_eth = paid.get("ETH", 0)
    paid_ogn = paid.get("OGN", 0)
    diff_eth = snapshots[0].vault_eth - snapshots[1].vault_eth
    diff_ogn = snapshots[0].vault_ogn - snapshots[1].vault_ogn

    if diff_eth < 0 and abs(diff_eth) != paid_eth:
        events.append(
            event_critical(
                "Unexpected FeeVault Balance Change   🥷",
                f"Vault balance changed by {format_ousd_human(diff_eth)} ETH "
                f"but {format_ousd_human(paid_eth)} ETH was paid out.",
                tags=EVENT_TAGS,
            )
        )
    elif diff_eth > 0:
        events.append(
            event_low(
                "FeeVault Received Funds   🏦",
                f"FeeVault received {format_ousd_human(diff_eth)} ETH.",
                tags=EVENT_TAGS,
            )
        )

    if diff_ogn < 0 and abs(diff_ogn) != paid_ogn:
        events.append(
            event_critical(
                "Unexpected FeeVault Balance Change   🥷",
                f"Vault balance changed by {format_ousd_human(diff_ogn)} OGN "
                f"but {format_ousd_human(paid_ogn)} OGN was paid out.",
                tags=EVENT_TAGS,
            )
        )
    elif diff_ogn > 0:
        events.append(
            event_low(
                "FeeVault Received Funds   🏦",
                f"FeeVault received {format_ousd_human(diff_ogn)} OGN.",
                tags=EVENT_TAGS,
            )
        )

    return events
