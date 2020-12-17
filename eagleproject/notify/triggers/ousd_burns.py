from eth_hash.auto import keccak
from eth_utils import encode_hex
from django.db.models import Q
from core.models import Log
from notify.events import event_normal

ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"
ONE_ADDRESS = "0x0000000000000000000000000000000000000001"

SIG_EVENT_REDEEM = encode_hex(keccak(b"Redeem(address,uint256)"))


def get_tx_logs(tx_hash):
    return Log.objects.filter(transaction_hash=tx_hash)


def is_redeem(transfer):
    """ Check if a transfer tx is part of a redeem

    NOTE: event_name on the Log model is not currently populated
    """
    tx_hash = str(transfer.tx_hash_id)
    logs = get_tx_logs(tx_hash)
    return any(map(lambda l: l.topic_0 == SIG_EVENT_REDEEM, logs))


def get_burns(new_transfers):
    """ Get all the burns since the given block number """
    if not new_transfers:
        return []

    burns = new_transfers.filter(
        # Common burn addresses
        Q(to_address=ZERO_ADDRESS) | Q(to_address=ONE_ADDRESS)
    )

    # We only care about the ones that aren't redemptions
    return filter(lambda b: is_redeem(b) is False, burns)


def run_trigger(new_transfers):
    """ Check OUSD transactions for burns """
    events = []

    """ Burns shouldn't happen too often, and only occur on redeems.

    TODO: This is probably too sensitive but will keep this for now """
    burns = get_burns(new_transfers)

    if burns:
        for burn in burns:
            events.append(
                event_normal(
                    "Burn   🔥",
                    "{} burned {} OUSD".format(
                        burn.from_address,
                        burn.amount
                    )
                )
            )

    return events
