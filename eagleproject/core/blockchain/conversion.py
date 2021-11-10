import math
from decimal import Decimal
from eth_utils import is_hex

from core.common import seconds_to_days
from core.blockchain.const import (
    E_18,
    COMPOUND_FOR_SYMBOL,
    CTOKEN_DECIMALS,
    DECIMALS_FOR_SYMBOL,
    BLOCKS_PER_DAY
)

from core.blockchain.rpc import (
    exchangeRateStored,
    rebasing_credits_per_token,
)


def ctoken_to_underlying(symbol, ctoken_amount, block="latest"):
    """ Convert an amount of cTokens to the underlying supply """
    underlying_deimals = DECIMALS_FOR_SYMBOL[symbol]
    exchange_rate = exchangeRateStored(COMPOUND_FOR_SYMBOL[symbol], block)
    return ctoken_amount * exchange_rate * Decimal(math.pow(
        10,
        CTOKEN_DECIMALS - underlying_deimals
    ))


def calc_apy(daily_rate, days):
    """ Calculate the APY for a given duration and rate as given by OGN Staking
    contract """

    yearly_rate = Decimal(daily_rate) * Decimal(365)

    return yearly_rate / Decimal(days)


def human_duration_yield(duration, rate):
    """ Take duration and rate as given in a tx or event and return human-useful
    values of days, APY """

    if type(duration) == str:
        if not is_hex(duration):
            raise ValueError('Unexpected value for duration')
        duration = int(duration, 16)

    if type(rate) == str:
        if not is_hex(rate):
            raise ValueError('Unexpected value for rate')
        rate = int(rate, 16)

    # Convert duration from seconds to days
    days = seconds_to_days(duration)

    # Scale from false-decimal to actual
    daily_rate = Decimal(rate / E_18)

    # Calculate Yield for the duration
    apy = calc_apy(daily_rate, days)

    return days, apy
