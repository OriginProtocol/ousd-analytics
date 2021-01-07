""" Strategy Deposit/Withdraw

Events:
- Deposit(address indexed _asset, address _pToken, uint256 _amount)
- Withdrawal(address indexed _asset, address _pToken, uint256 _amount)
"""
from django.db.models import Q
from eth_utils import decode_hex
from eth_abi import decode_single

from core.blockchain import SYMBOL_FOR_CONTRACT, CONTRACT_ADDR_TO_NAME
from core.common import format_token_human
from core.sigs import SIG_EVENT_DEPOSIT, SIG_EVENT_WITHDRAWAL
from notify.events import event_low


def get_events(logs):
    """ Get events """
    return logs.filter(
        Q(topic_0=SIG_EVENT_DEPOSIT)
        | Q(topic_0=SIG_EVENT_WITHDRAWAL)
    ).order_by('block_number')


def run_trigger(new_logs):
    """ Template trigger """
    events = []

    for ev in get_events(new_logs):
        asset = decode_single('(address)', decode_hex(ev.topic_1))[0]
        ptoken, amount = decode_single('(address,uint256)', decode_hex(ev.data))

        asset_name = SYMBOL_FOR_CONTRACT.get(asset, asset)
        contract_name = CONTRACT_ADDR_TO_NAME.get(ev.address, ev.address)

        if ev.topic_0 == SIG_EVENT_DEPOSIT:
            events.append(
                event_low(
                    "Deposit   🔼",
                    "{} {} was deposited to the {}\n\n".format(
                        format_token_human(asset_name, amount),
                        asset_name,
                        contract_name,
                    )
                )
            )

        elif ev.topic_0 == SIG_EVENT_WITHDRAWAL:
            events.append(
                event_low(
                    "Withdrawal   🔽",
                    "{} {} was withdrawn from the {}\n\n".format(
                        format_token_human(asset_name, amount),
                        asset_name,
                        contract_name,
                    )
                )
            )

        else:
            # Theoretically impossible
            raise Exception('Unexpected event')

    return events
