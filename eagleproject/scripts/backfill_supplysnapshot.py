import datetime

from core.blockchain.const import START_OF_OETH
from core.blockchain.rpc import latest_block
from core.blockchain.harvest.snapshots import ensure_supply_snapshot
from core.models import OriginTokens

def run():
    latest = latest_block()
    for block_number in range(START_OF_OETH, latest - 2):
        ensure_supply_snapshot(block_number, project=OriginTokens.OUSD)
        ensure_supply_snapshot(block_number, project=OriginTokens.OETH)
