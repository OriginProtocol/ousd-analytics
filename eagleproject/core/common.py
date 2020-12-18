from enum import Enum
from decimal import Decimal


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
