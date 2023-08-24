import datetime

from decimal import Decimal

from core.blockchain.addresses import OETH
from core.blockchain.const import START_OF_OETH
from core.blockchain.harvest.snapshots import ensure_supply_snapshot, ensure_asset
from core.models import OriginTokens, SupplySnapshot

from core.blockchain.rpc import origin_token_rebasing_credits, totalSupply, origin_token_non_rebasing_supply, rebasing_credits_per_token, OETHCurveAMOStrategy

def run(*script_args):
    start_block = int(script_args[0]) if len(script_args) > 0 else START_OF_OETH

    snapshots = SupplySnapshot.objects.filter(
        block_number__gte=start_block,
        project=OriginTokens.OETH
    ).order_by('-block_number').all()

    print("Found {} OETH Supply snapshots".format(len(snapshots)))
    for s in snapshots:
        print("Recomputing supply at block {}".format(s.block_number))
        oeth_amo_supply = OETHCurveAMOStrategy.get_underlying_balance(s.block_number).get("OETH", Decimal(0))
        s.non_rebasing_boost_multiplier = (s.computed_supply - oeth_amo_supply) / (s.computed_supply - s.non_rebasing_supply)
        s.save()

    print("Done.")
