""" Vault buffer related events """
from decimal import Decimal
from eth_utils import decode_hex
from eth_abi import decode_single
from core.blockchain.sigs import SIG_EVENT_BUFFER_UPDATE
from notify.events import event_normal

from core.blockchain.addresses import CONTRACT_ADDR_TO_NAME

def get_events(logs):
    """ Get events """
    return logs.filter(
        topic_0=SIG_EVENT_BUFFER_UPDATE
    ).order_by('block_number')


def run_trigger(new_logs):
    """ Template trigger """
    events = []

    for ev in get_events(new_logs):

        contract_name = CONTRACT_ADDR_TO_NAME.get(ev.address, ev.address)

        buffer_percent_bigint = decode_single(
            '(uint256)',
            decode_hex(ev.data)
        )[0]

        events.append(
            event_normal(
                "{} Buffer Updated   🤏".format(contract_name),
                "Vault buffer was changed to {}%".format(
                    # Always whole numbers?
                    (
                        Decimal(buffer_percent_bigint) / Decimal(1e18)
                    ) * Decimal(100)
                ),
                log_model=ev
            )
        )

    return events
