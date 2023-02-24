from datetime import ( datetime, timedelta, timezone )

from core.blockchain.harvest.blocks import (
    ensure_day_by_block,
    ensure_day,
)

from core.blockchain.rpc import (
    latest_block,
)

from core.blockchain.strategies import STRATEGIES

from core.blockchain.harvest.yield_proof.strategy_process import (
    create_yield_strategy,
)

# all yield snapshots since block_number to present
def ensure_yield_snapshots_since_block(block_number):
    day = ensure_day_by_block(block_number)
    date = day.date
    while(date <= datetime.utcnow().date()):
        ensure_yield_snapshot(day)
        date = date + timedelta(days=1)

# yield snapshot at block number
def ensure_yield_snapshot_at_block(block_number):
    day = ensure_day_by_block(block_number)
    ensure_yield_snapshot(day)

def ensure_yield_snapshot(day):
    start_day_block, end_day_block = __get_day_block_range(day)

    for strategy_key in STRATEGIES.keys():
        strategyInfo = STRATEGIES[strategy_key]
        if (strategyInfo['POY_PROCESS']):

            strategy = create_yield_strategy(
                strategy_key,
                strategyInfo['ADDRESS'],
                start_day_block,
                end_day_block
            )
            print("Strategy: ", strategy)
    

# get block range for a given day. If the day is:
#   - today -> end block range is current block time
#   - not today -> end block is the starting block of the next day - 1
def __get_day_block_range(day):
    day_is_today = datetime.utcnow().date() == day.date
    if day_is_today:
        return [day.block_number, latest_block()]
    else:

        date_after = datetime(day.date.year, day.date.month, day.date.day + 1)
        day_after = ensure_day(date_after)
        return [day.block_number, day_after.block_number - 1]
