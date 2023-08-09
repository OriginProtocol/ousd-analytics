""" Trigger for GovernorBravi implementation change """
from eth_utils import decode_hex
from eth_abi import decode_single

from core.blockchain.addresses import (
    COMPOUND_GOVERNOR_BRAVO, 
    FLUX_DAO,
    CONTRACT_ADDR_TO_NAME,
)
from core.blockchain.sigs import SIG_EVENT_NEW_IMPLEMENTATION_BRAVO
from notify.events import event_high

DISCORD_EMBED_DESCRIPTION_LIMIT = 2048

def get_events(logs):
    """ Get Mint/Redeem events """
    return logs.filter(address__in=[COMPOUND_GOVERNOR_BRAVO, FLUX_DAO]).filter(
        topic_0=SIG_EVENT_NEW_IMPLEMENTATION_BRAVO
    ).order_by('block_number')


def run_trigger(new_logs):
    """ Compound Timelock changes """
    events = []

    for ev in get_events(new_logs):
        old_address, new_address = decode_single(
            "(address,address)",
            decode_hex(ev.data)
        )
        new_link = 'https://etherscan.io/address/{}'.format(new_address)

        contract_name = CONTRACT_ADDR_TO_NAME.get(ev.address, ev.address)

        events.append(event_high(
            "{} implementation upgraded   🗳️ ⏫".format(contract_name),
            "{} implementation changed from {} to [{}]({})".format(
                contract_name, old_address, new_address, new_link
            ),
            log_model=ev
        ))

    return events
