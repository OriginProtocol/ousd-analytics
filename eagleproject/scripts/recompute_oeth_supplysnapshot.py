import datetime

from decimal import Decimal

from core.blockchain.addresses import OETH
from core.blockchain.const import START_OF_OETH
from core.blockchain.harvest.snapshots import ensure_supply_snapshot, ensure_asset
from core.models import OriginTokens, SupplySnapshot

from core.blockchain.rpc import origin_token_rebasing_credits, totalSupply, origin_token_non_rebasing_supply, rebasing_credits_per_token

def run(*script_args):
    start_block = 17249890 # Block when Curve AMO strategy was deployed 

    snapshots = SupplySnapshot.objects.filter(
        block_number__gte=start_block,
        project=OriginTokens.OETH
    ).order_by('-block_number').all()

    print("Found {} OETH Supply snapshots".format(len(snapshots)))
    for s in snapshots:
        print("Recomputing supply at block {}".format(s.block_number))

        # ETH asset doesn't exist. The other assets aren't affected.
        # OETH is the only one we need to delete and recompute
        ensure_asset("OETH", s.block_number, OriginTokens.OETH).delete()

        eth = ensure_asset("ETH", s.block_number, OriginTokens.OETH).total()
        weth = ensure_asset("WETH", s.block_number, OriginTokens.OETH).total()
        frxeth = ensure_asset("FRXETH", s.block_number, OriginTokens.OETH).total()
        reth = ensure_asset("RETH", s.block_number, OriginTokens.OETH).total()
        steth = ensure_asset("STETH", s.block_number, OriginTokens.OETH).total()
        oeth = ensure_asset("OETH", s.block_number, OriginTokens.OETH).total()

        s.credits = origin_token_rebasing_credits(s.block_number, contract=OETH) + s.non_rebasing_credits

        s.computed_supply = oeth + steth + reth + frxeth + weth + eth
        s.reported_supply = totalSupply(OETH, 18, s.block_number)
        s.non_rebasing_supply = origin_token_non_rebasing_supply(s.block_number, contract=OETH)

        if s.computed_supply == 0 and s.credits == 0:
            s.credits_ratio = 0
        else:
            s.credits_ratio = s.computed_supply / s.credits

        future_fee = (s.computed_supply - s.reported_supply) * Decimal(0.2)
        next_rebase_supply = (
            s.computed_supply - s.non_rebasing_supply - future_fee
        )
        if next_rebase_supply == 0 and s.credits == 0:
            s.rebasing_credits_ratio = 0
        else:
            s.rebasing_credits_ratio = next_rebase_supply / s.credits
        s.rebasing_credits_per_token = rebasing_credits_per_token(s.block_number, contract=OETH)

        s.save()

    print("Done.")
