from eth_hash.auto import keccak
from eth_utils import encode_hex, decode_hex
from eth_abi import decode_single
from notify.events import event_high

SIG_EVENT_ASSET_SUPPORTED = encode_hex(keccak(b"AssetSupported(address)"))


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
        events.append(
            event_high(
                "New asset supported    🆕",
                "A new asset can be used to mint OUSD: "
                "https://etherscan.io/token/{}".format(
                    asset_address,
                )
            )
        )

    return events
