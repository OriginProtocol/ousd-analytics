import datetime

from decimal import Decimal
from core.models import OriginTokens, SupplySnapshot
from core.blockchain.rpc import OETHCurveAMOStrategy, OUSDMetaStrategy
from core.blockchain.harvest.snapshots import ensure_asset

def run(*script_args):
    snapshots = SupplySnapshot.objects.filter(non_rebasing_boost_multiplier=0).order_by('-block_number').all()

    print("Found {} Supply snapshots".format(len(snapshots)))
    for s in snapshots:
        if s.project == OriginTokens.OETH:
            print("Computing OETH Boost multiplier at block {}".format(s.block_number))
            try:
                oeth = ensure_asset("OETH", s.block_number, project=OriginTokens.OETH)
                amo_supply = oeth.get_strat_holdings("oeth_curve_amo")
            except Exception as e:
                print(e)
                print("Reading from on-chain for block {}".format(s.block_number))
                amo_supply = OETHCurveAMOStrategy.get_underlying_balance(s.block_number).get("OETH", Decimal(0))
        elif s.project == OriginTokens.OUSD:
            print("Computing OUSD Boost multiplier at block {}".format(s.block_number))
            try:
                ousd = ensure_asset("OUSD", s.block_number, project=OriginTokens.OUSD)
                amo_supply = ousd.get_strat_holdings("ousd_metastrat")
            except Exception as e:
                print(e)
                print("Reading from on-chain for block {}".format(s.block_number))
                amo_supply = OUSDMetaStrategy.get_underlying_balance(s.block_number).get("OUSD", Decimal(0))
                
        s.non_rebasing_boost_multiplier = (s.computed_supply - amo_supply) / (s.computed_supply - s.non_rebasing_supply)
        s.save()

    print("Done.")
