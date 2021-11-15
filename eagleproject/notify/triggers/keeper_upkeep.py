from eth_abi import decode_single
from eth_utils import decode_hex
from django.db.models import Q
from core.common import format_token_human
from core.blockchain.const import OUSD_KEEPER_UPKEEP_ID
from core.blockchain.sigs import (
    EVENT_KEEPER_UPKEEP_PERFORMED,
    EVENT_KEEPER_UPKEEP_CANCELLED,
    EVENT_KEEPER_FUNDS_ADDED,
    EVENT_KEEPER_FUNDS_WITHDRAWN,
)
from notify.events import event_normal


def get_upkeep_events(logs):
    """ Get chainlink KeeperRegistry upkeep events """
    return logs.filter(
        Q(topic_0=EVENT_KEEPER_UPKEEP_PERFORMED)
        | Q(topic_0=EVENT_KEEPER_UPKEEP_CANCELLED)
        | Q(topic_0=EVENT_KEEPER_FUNDS_ADDED)
        | Q(topic_0=EVENT_KEEPER_FUNDS_WITHDRAWN)
    ).order_by("block_number")


def run_trigger(new_logs):
    """ Look for mints and redeems """
    events = []

    for ev in get_upkeep_events(new_logs):
        if ev.topic_0 == EVENT_KEEPER_UPKEEP_PERFORMED:
            """
            event UpkeepPerformed(
                uint256 indexed id,
                bool indexed success,
                address indexed from,
                uint96 payment,
                bytes performData
            );
            """
            _id = decode_single("(uint256)", decode_hex(ev.topic_1))[0]
            success = decode_single("(bool)", decode_hex(ev.topic_2))[0]
            from_address = decode_single("(address)", decode_hex(ev.topic_3))[0]
            payment, _ = decode_single("(uint96,bytes)", decode_hex(ev.data))

            if _id != OUSD_KEEPER_UPKEEP_ID:
                continue

            success_msg = "Successfully" if success else "Unsuccessfully"
            payment_formatted = format_token_human("LINK", payment)

            events.append(
                event_normal(
                    f"{success_msg} Performed OUSD Upkeep    🔗",
                    f"Upkeep for OUSD was performed {success_msg.lower()} by "
                    f"{from_address} and received payment of "
                    f"{payment_formatted} LINK",
                    log_model=ev,
                )
            )

        elif ev.topic_0 in EVENT_KEEPER_UPKEEP_CANCELLED:
            """
            event UpkeepCanceled(
                uint256 indexed id,
                uint64 indexed atBlockHeight
            );
            """
            _id = decode_single("(uint256)", decode_hex(ev.topic_1))[0]
            block_number = decode_single("(uint64)", decode_hex(ev.topic_2))[0]

            if _id != OUSD_KEEPER_UPKEEP_ID:
                continue

            events.append(
                event_normal(
                    f"OUSD Upkeep #{OUSD_KEEPER_UPKEEP_ID} Cancelled    🔗☠️",
                    f"OUSD Upkeep with ID {OUSD_KEEPER_UPKEEP_ID} has been "
                    f"cancelled as of block #{block_number}.",
                    log_model=ev,
                )
            )

        elif ev.topic_0 == EVENT_KEEPER_FUNDS_ADDED:
            """
            event FundsAdded(
                uint256 indexed id,
                address indexed from,
                uint96 amount
            );
            """
            _id = decode_single("(uint256)", decode_hex(ev.topic_1))[0]
            from_address = decode_single("(address)", decode_hex(ev.topic_2))[0]
            amount = decode_single("(uint96)", decode_hex(ev.data))[0]

            if _id != OUSD_KEEPER_UPKEEP_ID:
                continue

            amount_human = format_token_human("LINK", amount)

            events.append(
                event_normal(
                    f"OUSD Upkeep #{OUSD_KEEPER_UPKEEP_ID} Funded    🫴🔗",
                    f"Funds added ({amount_human} LINK) for OUSD Upkeep with "
                    f"ID {OUSD_KEEPER_UPKEEP_ID} by {from_address}.",
                    log_model=ev,
                )
            )

        elif ev.topic_0 == EVENT_KEEPER_FUNDS_WITHDRAWN:
            """
            event FundsWithdrawn(
                uint256 indexed id,
                uint256 amount,
                address to
            );
            """
            _id = decode_single("(uint256)", decode_hex(ev.topic_1))[0]
            amount, to_address = decode_single(
                "(uint256,address)", decode_hex(ev.data)
            )

            if _id != OUSD_KEEPER_UPKEEP_ID:
                continue

            amount_human = format_token_human("LINK", amount)

            events.append(
                event_normal(
                    f"OUSD Upkeep #{OUSD_KEEPER_UPKEEP_ID} Defunded    🫳🔗",
                    f"Funds removed ({amount_human} LINK) for OUSD Upkeep with "
                    f"ID {OUSD_KEEPER_UPKEEP_ID} and sent to {to_address}.",
                    log_model=ev,
                )
            )

    return events
