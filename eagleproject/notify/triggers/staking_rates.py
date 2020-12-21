from datetime import timedelta
from decimal import Decimal
from eth_hash.auto import keccak
from eth_utils import encode_hex
from eth_abi import decode_single
from django.db.models import Q
from notify.events import event_high

SIG_EVENT_NEW_DURATIONS = encode_hex(
    keccak(b"NewDurations(address,uint256[])")
)
SIG_EVENT_NEW_RATES = encode_hex(keccak(b"NewRates(address,uint256[])"))
FALSE_256BIT = "0x0000000000000000000000000000000000000000000000000000000000000000"
TRUE_256BIT = "0x0000000000000000000000000000000000000000000000000000000000000001"


def get_rates_events(logs):
    """ Get NewRates events """
    return logs.filter(
        topic_0=SIG_EVENT_NEW_RATES
    ).order_by('block_number')


def get_durations_event(logs, tx_hash):
    """ NewDurations is triggered during the same transaction and needs to match
    the NewRates one to figure out how they relate """
    for log in logs.filter(tx_hash=tx_hash).order_by('block_number'):
        if log.topic_0 == SIG_EVENT_NEW_DURATIONS:
            return log
    return None


def run_trigger(new_logs):
    """ Template trigger """
    events = []

    for ev in get_rates_events(new_logs):
        duration_event = get_durations_event(ev.transaction_hash)
        rates = decode_single("(uint256[])", ev.data)
        durations = decode_single("(uint256[])", duration_event.data)

        durations_string = ""

        for i, duration in enumerate(durations):
            # Percentage of return as an 18-decimal int
            rate = Decimal(rates[i]) / Decimal(1e18)
            duration_dt = timedelta(seconds=duration)
            durations_string += "\n - {} days @ {}".format(
                duration_dt.days,
                rate
            )

        events.append(
            event_high("OGN Staking Rates Changed   🧮", durations_string)
        )

    return events
