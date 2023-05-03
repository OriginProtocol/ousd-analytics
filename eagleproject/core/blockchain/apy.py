from decimal import Decimal
from core.blockchain.rpc import (
    rebasing_credits_per_token,
)
from core.blockchain.harvest.snapshots import (
    latest_snapshot,
    latest_snapshot_block_number
)
from core.blockchain.harvest.transactions import (
    get_rebasing_credits_per_token
)
from core.blockchain.const import (
    BLOCKS_PER_DAY
)
from core.models import OriginTokens
from django.core.exceptions import ObjectDoesNotExist


PREV_APR = None

# if block is None, the latest block shall be considered
def get_trailing_apr(block=None, days=30.00, project=OriginTokens.OUSD):
    """
    Calculates the APR by using the OUSD rebase ratio. 

    This has the upside that it's simple to calculate and exactly matches 
    user's balance changes. 

    It has the downside that the number it pulls from only gets updated
    on rebases, making this method less accurate. It's bit iffy using it
    on only one day, but that's the data we have at the moment.
    """

    # Check cache first
    global PREV_APR
    if PREV_APR and block is None:
        good_to, apr = PREV_APR
        if good_to > datetime.datetime.today():
            return apr

    # Calculate
    block = block if block is not None else latest_snapshot_block_number(project)
    current = get_rebasing_credits_per_token(block, project)
    past = get_rebasing_credits_per_token(int(block - BLOCKS_PER_DAY * days), project)

    ratio = Decimal(float(past) / float(current))
    apr = ((ratio - Decimal(1)) * Decimal(100) * Decimal(365.25) / Decimal(days))

    # Save to cache
    if block is None:
        good_to = datetime.datetime.today() + datetime.timedelta(minutes=5)
        PREV_APR = [good_to, apr]
    return apr

# if block is None, the latest block shall be considered
def get_trailing_apy(block=None, days=30.00, project=OriginTokens.OUSD):
    # We don't have enough data to calculate APR on OETH
    try:
        apr = Decimal(get_trailing_apr(block, days, project))
    except ObjectDoesNotExist:
        return 0
    apy = to_apy(apr, days)
    return round(apy, 2)

def to_apy(apr, days=30.00):
    periods_per_year = Decimal(365.25 / days)
    return ((1 + apr / periods_per_year / 100) ** periods_per_year - 1) * 100