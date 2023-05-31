from core.models import Transaction
from core.blockchain.addresses import CONTRACT_ADDR_TO_NAME
from core.blockchain.const import ETHERSCAN_CONTRACTS
from core.blockchain.harvest.transactions import (
    ensure_transaction_and_downstream,
)
from notify.events import event_high


def tx_error_event(tx_hash, contract_name, block_number=0, transaction_index=0):
    """Create an event for a transaction error

    TODO: Make this more intelligent and informative
    """
    return event_high(
        "Transaction Error   🛑",
        "A transaction error has occurred on the {} contract\n\n"
        "https://etherscan.io/tx/{}".format(
            contract_name,
            tx_hash,
        ),
        block_number=block_number,
        transaction_index=transaction_index,
    )


def get_failed_transactions(address, start_block, end_block):
    """ Get all failed transactions between start and end blocks """
    return Transaction.objects.filter(
        data__to=address,
        receipt_data__status="0x0",
        block_number__gt=start_block,
        block_number__lte=end_block,
    )


def run_trigger(latest_block, transaction_cursor):
    """ Template trigger """
    events = []

    for address in ETHERSCAN_CONTRACTS:
        name = CONTRACT_ADDR_TO_NAME.get(address, "Unknown")

        for tx in get_failed_transactions(
            address, transaction_cursor.block_number, latest_block
        ):
            # Make sure it goes into the DB
            ensure_transaction_and_downstream(tx.tx_hash)

            # Create an event
            events.append(
                tx_error_event(
                    tx.tx_hash,
                    name,
                    block_number=tx.block_number,
                    transaction_index=tx.data.get("transaction_index", 0),
                )
            )

    return events
