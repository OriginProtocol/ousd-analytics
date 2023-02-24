from datetime import datetime, timedelta, timezone
from core.blockchain.rpc import (
    get_block,
)
from core.logging import get_logger
from core.models import (
    Block,
    Day
)

from django.db.utils import IntegrityError

logger = get_logger(__name__)


def ensure_block(block_number):
    stored_block = Block.objects.filter(block_number=block_number).first()
    if stored_block is not None:
        return stored_block
    
    raw_block = get_block(block_number)
    block_time = datetime.fromtimestamp(
        int(raw_block["timestamp"], 16),
        timezone.utc
    )

    block = Block(block_number=block_number, block_time=block_time)
    try:
        block.save()
    except IntegrityError:
        # do nothing... when multiple threads are fetching transactions sometimes 2 threads
        # try to save the same block with the same number. We just ignore this type of error.
        print("Warning: caught an error trying to save 2 blocks with the same block_number")

    return block

# anything before 26100 seconds into the UTC (7h15m+UTC) is considered a day before. Anything after
# that time is considered the same day as UTC
def ensure_day_by_block(block_number):
    block = ensure_block(block_number)
    total_seconds = block.block_time.hour * 3600 + block.block_time.minute * 60 + block.block_time.second
    return ensure_day(block.block_time - timedelta(days=1) if total_seconds <= 26100 else block.block_time)

def ensure_day(d):
    #2023-02-21 00:08
    """
        Find the block number to represent the start of a day. This is a time 1-15 minutes
        after the daily rebase is scheduled to happen.
    
        OUSDKeeper Chainlink contract that is responsible for the performing upkeep (rebase)
        has windowEnd configured to: 26065.

        Uses a bisecting binary search to home in on the correct block.
            ... You could probably be faster by using an estimator to get close first.
        Requires there to be a block stored in the system before and after the target.
            ... More code could easily remove this restriction.
    """
    stored_day = Day.objects.filter(date=d.date()).first()
    if stored_day is not None:
        return stored_day
    d = datetime(d.year, d.month, d.day) # Zero seconds, keep timezone
    # Offset for the window on the next day
    target = (d + timedelta(seconds=26100)).replace(tzinfo=timezone.utc)
    _blocks = Block.objects.filter(block_time__gte = target).order_by('block_time')
    after_block = _blocks[0] if len(_blocks) > 0 else None

    _blocks = Block.objects.filter(block_time__lt = target).order_by('-block_time')
    before_block = _blocks[0] if len(_blocks) > 0 else None




    if after_block is None or before_block is None:
        return None

    while after_block.block_number - before_block.block_number > 2:
        difference = after_block.block_number - before_block.block_number
        pivot_block_number = after_block.block_number - int(difference / 2)
        pivot = ensure_block(pivot_block_number)
        if pivot.block_time > target:
            after_block = pivot
        else:
            before_block = pivot

    end_day_block = after_block

    day = Day(date=d.date(), block_number=end_day_block.block_number)
    day.save()
    return day