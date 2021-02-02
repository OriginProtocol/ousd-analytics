from datetime import datetime
from core.blockchain.rpc import (
    get_block,
)
from core.logging import get_logger
from core.models import (
    Block,
)

logger = get_logger(__name__)


def ensure_block(block_number):
    blocks = list(Block.objects.filter(block_number=block_number))
    if len(blocks) > 0:
        return blocks[0]
    else:
        raw_block = get_block(block_number)
        block_time = datetime.utcfromtimestamp(int(raw_block["timestamp"], 16))
        block = Block(block_number=block_number, block_time=block_time)
        block.save()
        return block
