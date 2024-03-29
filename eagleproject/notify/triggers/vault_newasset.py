from eth_utils import decode_hex
from eth_abi import decode_single
from core.blockchain.sigs import SIG_EVENT_ASSET_SUPPORTED
from notify.events import event_high

from core.blockchain.addresses import CONTRACT_ADDR_TO_NAME

def get_asset_events(logs):
    """ Get AssetSupported events """
    return logs.filter(
        topic_0=SIG_EVENT_ASSET_SUPPORTED
    ).order_by('block_number')


def run_trigger(new_logs):
    """ Template trigger """
    events = []

    for ev in get_asset_events(new_logs):
        asset_address = decode_single('(address)', decode_hex(ev.data))[0]
        contract_name = CONTRACT_ADDR_TO_NAME.get(ev.address, ev.address)

        events.append(
            event_high(
                "New asset supported    🆕",
                "A new asset can be used to mint with {}: https://etherscan.io/token/{}".format(
                    contract_name,
                    asset_address,
                ),
                log_model=ev
            )
        )

    return events
