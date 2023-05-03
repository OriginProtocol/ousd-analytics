import datetime

# from core.blockchain.const import START_OF_OETH
from core.blockchain.rpc import latest_block
from core.blockchain.harvest.snapshots import ensure_supply_snapshot
from core.models import OriginTokens, SupplySnapshot

def run(*script_args):
    latest = latest_block()

    bad_block = 17171685 # The block from which the data got bad
    
    start_block = int(script_args[0]) if len(script_args) > 0 else bad_block # The block from which the data got bad

    print("Deleting older rows from DB")
    SupplySnapshot.objects.filter(
        block_number__gte=start_block
    ).delete()

    print("Target block range to backfill: {} to {}".format(start_block, latest - 2))
    for block_number in range(start_block, latest - 2):
        try:
            print("Taking snapshot of OUSD Supply on Block {}".format(block_number))
            ensure_supply_snapshot(block_number, project=OriginTokens.OUSD)
        except:
            print("Failed to fetch block")

        try:
            print("Taking snapshot of OETH Supply on Block {}".format(block_number))
            ensure_supply_snapshot(block_number, project=OriginTokens.OETH)
        except:
            print("Failed to fetch block")

    print("Done.")
