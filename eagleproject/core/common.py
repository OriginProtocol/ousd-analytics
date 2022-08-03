import multihash
from math import pow
from enum import Enum
from decimal import Decimal
from eth_utils import remove_0x_prefix

from core.blockchain.const import DECIMALS_FOR_SYMBOL

SECONDS_IN_DAY = 24 * 60 * 60


class Direction(Enum):
    GAIN = "gain"
    LOSS = "loss"


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


def format_usd_human(value, places=4):
    if value == Decimal(0):
        return "0"

    return f"{value:,.{places}f}".rstrip("0").rstrip(".")


def format_token_human(symbol, value, places=4):
    if value == Decimal(0):
        return "0"

    value = Decimal(value) / Decimal(pow(10, DECIMALS_FOR_SYMBOL[symbol]))

    return f"{value:,.{places}f}".rstrip("0").rstrip(".")


# Backwards compat, mostly
format_ousd_human = format_usd_human
format_ogn_human = format_usd_human
format_decimal = format_usd_human


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
    if hex_hash.startswith("0x"):
        hex_hash = remove_0x_prefix(hex_hash)
    if not hex_hash.startswith("1220"):
        hex_hash = "1220" + hex_hash
    return multihash.to_b58_string(multihash.from_hex_string(hex_hash))


def first(it, match):
    """ Find first element of iter to match match """
    if not callable(match):
        match = lambda x: x == match
    for i in it:
        if match(i):
            return i
    return None


def all_zero(iter):
    """ Check if all items in an iterable are 0 """
    for x in iter:
        if x != 0:
            return False
    return True


def truncate_elipsis(v, max_length=2048, elipsis=" ..."):
    """ Truncate a string to max_length and append elipsis to the end """
    if len(v) <= max_length:
        return v
    return v[: max_length - len(elipsis)] + elipsis


def format_timedelta(v):
    """ Format a timedelta object to a string """
    out = ""
    days = v.days
    hours, rem = divmod(v.seconds, 3600)
    minutes, seconds = divmod(rem, 60)

    if days:
        out += " {} days".format(days)
    if hours:
        out += " {} hours".format(hours)
    if minutes:
        out += "{} minutes".format(minutes)
    if seconds:
        out += "{} seconds".format(seconds)

    return out.strip()
