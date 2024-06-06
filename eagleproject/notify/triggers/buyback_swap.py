""" BuyBack swap event triggers """
from eth_utils import decode_hex
from eth_abi import decode_single

from core.models import Log

from core.blockchain.const import OETH_BUYBACK_BLOCK

from core.blockchain.addresses import OGV, OETH, OUSD, CVX, OGV_BUYBACK_LEGACY, OUSD_BUYBACK_PROXY, OETH_BUYBACK_PROXY, REWARDS_SOURCE, OUSD, CONTRACT_ADDR_TO_NAME
from core.blockchain.sigs import TRANSFER, SIG_EVENT_OTOKEN_BUYBACK
from core.common import format_token_human
from notify.events import event_low

def get_legacy_events(logs):
    """ Get events """
    return logs.filter(
        address=OUSD,
        topic_0=TRANSFER,
        topic_1__in=[
            get_long_address(OGV_BUYBACK_LEGACY),
            get_long_address(OUSD_BUYBACK_PROXY),
        ]
    ).order_by('block_number')

def get_swap_events(logs):
    """ Get events """
    return logs.filter(
        topic_0=SIG_EVENT_OTOKEN_BUYBACK,
    ).order_by('block_number')

def run_trigger(new_logs):
    """ Template trigger """

    if len(new_logs) <= 0:
        return []

    events = []
    block_number = new_logs[0].block_number

    if block_number > OETH_BUYBACK_BLOCK:
        for ev in get_swap_events(new_logs):
            otoken = decode_single("(address)", decode_hex(ev.topic_1))[0]
            dest_token = decode_single("(address)", decode_hex(ev.topic_2))[0]
            (amount_in, amount_out) = decode_single(
                "(uint256,uint256)",
                decode_hex(ev.data)
            )

            otoken_symbol = "OETH" if otoken == OETH else "OUSD"

            if dest_token == CVX:
                events.append(
                    event_low(
                        "{} BuyBack        🔄".format(otoken_symbol),
                        "Swapped {} {} for {} CVX and locked it for voting power".format(
                            format_token_human(otoken_symbol, amount_in), 
                            otoken_symbol,
                            format_token_human('CVX', amount_out),
                        ),
                        log_model=ev
                    )
                )
            elif dest_token == OGV:
                events.append(
                    event_low(
                        "{} BuyBack        🔄".format(otoken_symbol),
                        "Swapped {} {} for {} OGV and depositted it to the RewardsSource contract".format(
                            format_token_human(otoken_symbol, amount_in), 
                            otoken_symbol,
                            format_token_human('OGV', amount_out),
                        ),
                        log_model=ev
                    )
                )
            elif dest_token == OGN:
                events.append(
                    event_low(
                        "{} BuyBack        🔄".format(otoken_symbol),
                        "Swapped {} {} for {} OGN and depositted it to the RewardsSource contract".format(
                            format_token_human(otoken_symbol, amount_in), 
                            otoken_symbol,
                            format_token_human('OGN', amount_out),
                        ),
                        log_model=ev
                    )
                )
            else:
                events.append(
                    event_low(
                        "{} BuyBack        🔄".format(otoken_symbol),
                        "Swapped {} {} for {} {}".format(
                            format_token_human(otoken_symbol, amount_in), 
                            otoken_symbol,
                            format_token_human(otoken_symbol, amount_out),
                            CONTRACT_ADDR_TO_NAME[dest_token],
                        ),
                        log_model=ev
                    )
                )
    else:
        # For legacy Buyback contracts
        for ev in get_legacy_events(new_logs):
            swap_log = get_ogv_swap_log(ev.transaction_hash)

            if swap_log is None:
                continue

            ousd_out = decode_single('(uint256)',decode_hex(ev.data))[0]
            ogv_in = decode_single('(uint256)',decode_hex(swap_log.data))[0]

            events.append(event_low(
                "OGV BuyBack        🔄",
                "Swapped {} OUSD for {} OGV and depositted to Rewards Source contract".format(
                    format_token_human('OUSD', ousd_out), 
                    format_token_human('OGV', ogv_in),
                ),
                log_model=ev
            ))

    return events

def get_ogv_swap_log(transaction_hash):
    return Log.objects.get(transaction_hash=transaction_hash,address=OGV,topic_2=get_long_address(REWARDS_SOURCE))

def get_long_address(address):
    return address.replace("0x", "0x000000000000000000000000")
