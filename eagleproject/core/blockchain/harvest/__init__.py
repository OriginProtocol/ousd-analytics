from core.blockchain.const import AAVE_ASSETS, COMPOUND_FOR_SYMBOL
from core.blockchain.harvest.snapshots import (
    ensure_3pool_snapshot,
    ensure_aave_snapshot,
    ensure_asset,
    ensure_ctoken_snapshot,
    ensure_supply_snapshot,
    ensure_staking_snapshot,
    ensure_story_staking_snapshot,
    ensure_oracle_snapshot,
)
from core.blockchain.harvest.transactions import (
    ensure_all_transactions,
    ensure_latest_logs,
    download_logs_from_contract,
)

from core.blockchain.harvest.yield_proof import (
    ensure_yield_snapshot_at_block,
)
from core.models import OriginTokens

def refresh_transactions(block_number):
    ensure_latest_logs(block_number)
    ensure_all_transactions(block_number)


def snap(block_number):
    """ Take snapshots of assets """
    # OUSD
    ensure_asset("DAI", block_number)
    ensure_asset("USDT", block_number)
    ensure_asset("USDC", block_number)
    ensure_asset("COMP", block_number)
    ensure_supply_snapshot(block_number)
    ensure_staking_snapshot(block_number)
    ensure_story_staking_snapshot(block_number)
    ensure_oracle_snapshot(block_number)

    for symbol in COMPOUND_FOR_SYMBOL:
        ensure_ctoken_snapshot(symbol, block_number)

    for symbol in AAVE_ASSETS:
        ensure_aave_snapshot(symbol, block_number)

    ensure_3pool_snapshot(block_number)

    # OETH
    ensure_asset("ETH", block_number, OriginTokens.OETH)
    ensure_asset("WETH", block_number, OriginTokens.OETH)
    ensure_asset("FRXETH", block_number, OriginTokens.OETH)
    ensure_asset("RETH", block_number, OriginTokens.OETH)
    ensure_asset("STETH", block_number, OriginTokens.OETH)
    ensure_supply_snapshot(block_number, OriginTokens.OETH)

def reload_all(block_number):
    # TODO un-comment
    #refresh_transactions(block_number)
    #snap(block_number)
    #ensure_yield_snapshot_at_block(block_number)
    # 16673225 -> meta strategy reward tokens harvested
    # 16605149 -> morpho compound reward tokens harvested
    #download_logs_from_contract("0x5A4eEe58744D1430876d5cA93cAB5CcB763C037D", 16605148, 16605150)
    

    ensure_yield_snapshot_at_block(17448153, project=OriginTokens.OETH)
