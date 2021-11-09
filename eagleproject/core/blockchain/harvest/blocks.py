from datetime import datetime, timezone
from core.blockchain.rpc import (
    get_block,
)
from core.logging import get_logger
from core.models import (
    Block,
)

from django.db.utils import IntegrityError

logger = get_logger(__name__)


def ensure_block(block_number):
    blocks = list(Block.objects.filter(block_number=block_number))
    if len(blocks) > 0:
        return blocks[0]
    
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
