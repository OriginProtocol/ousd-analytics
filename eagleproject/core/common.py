import re
from math import pow
from enum import Enum
from decimal import Decimal
from eth_abi import decode_single

from core.blockchain import DECIMALS_FOR_SYMBOL

SIG_PATTERN = r'^([A-Za-z_0-9]+)\(([0-9A-Za-z_,]*)\)$'


class OrderedEnum(Enum):
    def __ge__(self, other):
        if self.__class__ is other.__class__:
            return self.value >= other.value
        return NotImplementedError("Unable to compare types")

    def __gt__(self, other):
        if self.__class__ is other.__class__:
            return self.value > other.value
        return NotImplementedError("Unable to compare types")

    def __le__(self, other):
        if self.__class__ is other.__class__:
            return self.value <= other.value
        return NotImplementedError("Unable to compare types")

    def __lt__(self, other):
        if self.__class__ is other.__class__:
            return self.value < other.value
        return NotImplementedError("Unable to compare types")

    def __str__(self):
        return self.name


class Severity(OrderedEnum):
    CRITICAL = 40
    HIGH = 30
    NORMAL = 20
    LOW = 10


def number_string_comma(v):
    """ Add comma formatting to integer strings """
    length = len(v)

    if length == 0:
        return 0

    if length < 3:
        return v

    out = ''

    # :-|
    for i, j in enumerate(reversed(range(len(v)))):
        if i % 3 == 0 and j != length - 1:
            out = ',' + out
        out = v[j] + out

    return out


def format_ousd_human(value, places=4):
    if value == Decimal(0):
        return '0'

    q = Decimal(10) ** -places  # 2 places --> '0.01'
    sign, digits, exp = value.quantize(q).as_tuple()

    return '{}.{}'.format(
        number_string_comma(''.join(map(str, digits[:exp]))),
        ''.join(map(str, digits[exp:])).rstrip('0') or '00'
    )


def format_token_human(symbol, value, places=4):
    if value == Decimal(0):
        return '0'

    value = Decimal(value) / Decimal(pow(10, DECIMALS_FOR_SYMBOL[symbol]))

    q = Decimal(10) ** -places  # 2 places --> '0.01'
    sign, digits, exp = value.quantize(q).as_tuple()

    return '{}.{}'.format(
        number_string_comma(''.join(map(str, digits[:exp]))),
        ''.join(map(str, digits[exp:])).rstrip('0') or '00'
    )


# In case we want this different in the future
format_ogn_human = format_ousd_human


def format_deimal(v):
    """ Format a Decimal to a string, stripping off unnecessary trailing zeros
    """
    sign, digits, price_exp = v.as_tuple()
    price_whole = digits[:price_exp] if len(digits) > abs(price_exp) else (0,)
    price_decimal = digits[price_exp:]
    dec_leftpad = abs(price_exp) - len(price_decimal)
    return "{}.{}{}".format(
        ''.join(map(str, price_whole)),
        '0' * dec_leftpad,
        ''.join(map(str, price_decimal)).rstrip('0')
    )


def decode_call(signature, calldata):
    """ Decode calldata for a given string signature """
    match = re.match(SIG_PATTERN, signature)

    if not match:
        # TODO: Better way to represent this?
        return '{}({})'.format(signature[:10], calldata)

    func = match.groups()[0]
    try:
        types_string = match.groups()[1]
    except IndexError:
        types_string = ""

    # Tag the arg types from the signature and decode calldata accordingly
    types = [x.strip() for x in types_string.split(',')]
    args = decode_single('({})'.format(','.join(types)), calldata)

    # Assemble a human-readable function call with arg values
    return '{}({})'.format(func, ','.join([str(v) for v in args]))


def decode_calls(signatures, calldatas):
    """ Decode multiple calldatas for given string signatures """
    calls = []

    for i, sig in enumerate(signatures):
        calls.append(decode_call(sig, calldatas[i]))

    return calls
