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

        eth = ensure_asset("ETH", s.block_number, OriginTokens.OETH).redeem_value()
        weth = ensure_asset("WETH", s.block_number, OriginTokens.OETH).redeem_value()
        frxeth = ensure_asset("FRXETH", s.block_number, OriginTokens.OETH).redeem_value()
        reth = ensure_asset("RETH", s.block_number, OriginTokens.OETH).redeem_value()
        steth = ensure_asset("STETH", s.block_number, OriginTokens.OETH).redeem_value()
        oeth = ensure_asset("OETH", s.block_number, OriginTokens.OETH).redeem_value()

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
        oeth_amo_supply = OETHCurveAMOStrategy.get_underlying_balance(s.block_number).get("OETH", Decimal(0))
        s.non_rebasing_boost_multiplier = (s.computed_supply - oeth_amo_supply) / (s.computed_supply - s.non_rebasing_supply)

        s.save()

    print("Done.")
