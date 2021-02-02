import math
from decimal import Decimal

from core.blockchain.const import COMPOUND_FOR_SYMBOL, CTOKEN_DECIMALS, DECIMALS_FOR_SYMBOL
from core.blockchain.rpc import exchangeRateStored


def ctoken_to_underlying(symbol, ctoken_amount, block="latest"):
    """ Convert an amount of cTokens to the underlying supply """
    underlying_deimals = DECIMALS_FOR_SYMBOL[symbol]
    exchange_rate = exchangeRateStored(COMPOUND_FOR_SYMBOL[symbol], block)
    return ctoken_amount * exchange_rate * Decimal(math.pow(
        10,
        CTOKEN_DECIMALS - underlying_deimals
    ))
