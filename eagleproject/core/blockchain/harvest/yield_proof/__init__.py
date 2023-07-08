from datetime import ( datetime, timedelta, timezone )

from core.blockchain.harvest.blocks import (
    ensure_day_by_block,
    ensure_day,
)

from core.blockchain.rpc import (
    latest_block,
)

from core.blockchain.strategies import (
    OUSD_STRATEGIES, OETH_STRATEGIES
)

from core.blockchain.harvest.yield_proof.strategy_process import (
    create_yield_strategy,
)

from core.models import OriginTokens

# all yield snapshots since block_number to present
def ensure_yield_snapshots_since_block(block_number):
    day = ensure_day_by_block(block_number)
    date = day.date
    while(date <= datetime.utcnow().date()):
        ensure_yield_snapshot(day)
        date = date + timedelta(days=1)

# yield snapshot at block number
def ensure_yield_snapshot_at_block(block_number, project):
    day = ensure_day_by_block(block_number)
    ensure_yield_snapshot(day, project=project)

def ensure_yield_snapshot(day, project):

    if project == OriginTokens.OUSD:
        for strategy_key in OUSD_STRATEGIES.keys():
            strategyInfo = OUSD_STRATEGIES[strategy_key]
            if (strategyInfo['POY_PROCESS']):
                # TODO: remove IF statement
                if strategy_key == 'morpho_comp_strat':
                    strategy = create_yield_strategy(
                        strategy_key,
                        strategyInfo['ADDRESS'],
                        strategyInfo['POY_ASSETS'],
                        day,
                        project=project
                    )

                    print("strat", strategy)
    else:
        for strategy_key in OETH_STRATEGIES.keys():
            strategyInfo = OETH_STRATEGIES[strategy_key]
            if (strategyInfo['POY_PROCESS']):
                # TODO: remove IF statement
                if strategy_key == 'oeth_curve_amo':
                    strategy = create_yield_strategy(
                        strategy_key,
                        strategyInfo['ADDRESS'],
                        strategyInfo['POY_ASSETS'],
                        day,
                        project=project
                    )

                    print("strat", strategy)


    
    


