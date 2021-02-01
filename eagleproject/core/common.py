import multihash
from math import pow
from enum import Enum
from decimal import Decimal
from eth_utils import remove_0x_prefix

from core.blockchain.const import DECIMALS_FOR_SYMBOL

SECONDS_IN_DAY = 24 * 60 * 60


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


def format_decimal(v, max_decimals=None):
    """ Format a Decimal to a string, stripping off unnecessary trailing zeros
    """
    sign, digits, price_exp = v.as_tuple()
    price_whole = digits[:price_exp] if len(digits) > abs(price_exp) else (0,)
    price_decimal = digits[price_exp:]
    dec_leftpad = abs(price_exp) - len(price_decimal)
    dec_string = "{}{}".format(
        '0' * dec_leftpad,
        ''.join(map(str, price_decimal)).rstrip('0')
    )

    if max_decimals and len(dec_string) > max_decimals:
        dec_string = dec_string[:max_decimals]

    return "{}.{}".format(
        number_string_comma(''.join(map(str, price_whole))),
        dec_string,
    )


def dict_append(d, k, v):
    """ Make sure a dict key is a list, then append to it """
    if k not in d or not isinstance(d[k], list):
        d[k] = list()
    d[k].append(v)
    return d


def seconds_to_days(v):
    return v / SECONDS_IN_DAY


def decode_ipfs_hash(hex_hash):
    """ Decode a Base58 IPFS hash from a 32 byte hex string """
    if hex_hash.startswith('0x'):
        hex_hash = remove_0x_prefix(hex_hash)
    if not hex_hash.startswith('1220'):
        hex_hash = '1220' + hex_hash
    return multihash.to_b58_string(
        multihash.from_hex_string(hex_hash)
    )


def first(it, match):
    """ Find first element of iter to match match """
    if not callable(match):
        match = lambda x: x == match
    for i in it:
        if match(i):
            return i
    return None
