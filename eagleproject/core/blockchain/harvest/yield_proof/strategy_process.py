from django.db.models import Q
import numpy as np
from core.models import (
    Log,
)

from core.blockchain.harvest.yield_proof.strategy import (
    BaseStrategyYield,
    BareYieldUnit,
    TokenBalance,
    YieldUnitList
)

from core.blockchain.rpc import (
    checkBalance,
)

from core.blockchain.const import (
    STRATEGY_REWARD_TOKEN_COLLECTED_TOPIC,
    STRATEGY_DEPOSIT_TOPIC,
    STRATEGY_WITHDRAWAL_TOPIC,
    CONTRACT_FOR_SYMBOL,
    DECIMALS_FOR_SYMBOL
)

def create_yield_strategy(name, strategy_address, asset_name_list, start_day_block, end_day_block):
    # these are all the relevant logs. Potentially even before start block and after
    # end block
    logs = get_relevant_logs(start_day_block, end_day_block, strategy_address)
    yield_units = build_yield_units(logs, [start_day_block, end_day_block], strategy_address, asset_name_list)

    average_token_balances, average_total = yield_units.average_token_balances()
    
    print("yield_units", yield_units, average_token_balances, average_total)

    return BaseStrategyYield(name, strategy_address, start_day_block, end_day_block)

# create build units out of logs. Blocks play as additional breaking points that split yield
# unit into 2.
def build_yield_units(logs, blocks, strategy_address, asset_name_list):
    all_blocks = list(np.unique(list(map(lambda log: log.block_number, logs)))) + blocks
    all_blocks.sort()

    yield_units = []
    for index, block_number in enumerate(all_blocks):
        # last block_number in all_blocks is the end interval of previous for loop
        # created BareYieldUnit
        if (index >= len(all_blocks) - 2):
            break;

        token_balances = []
        for asset_name in asset_name_list:
            asset_address = CONTRACT_FOR_SYMBOL[asset_name]
            decimals = DECIMALS_FOR_SYMBOL[asset_name]
            balance = checkBalance(strategy_address, asset_address, decimals, block_number)
            token_balances.append(TokenBalance(asset_address, balance))
        yield_units.append(BareYieldUnit(token_balances, block_number, all_blocks[index + 1]))
    return YieldUnitList(yield_units)


# To be able to calculate the exact yield of any strategy between 2 block numbers we need 
# a wider set of logs. Since harvest before the block range & harvest in the future affect the 
# yield calculation inside the block range. To illustrate (x axis is time) -> and in favour of 
# simplicity the strategy balance is constant (y axis): 
#  ↑
#  |
#  |
#  |
#  |  _______________________________________
#  |
#  |--t0---------t1----t2---t3--------→
#
#  Lets say we want to calculate exact daily yield of a strategy defined by start_time t1 and end_time
#  t3. The t0 and t2 are reward harvest events. The calculation process is:
#
#   - in the above case there are no harvest events happening after t3, so no look ahead and calculate
#     actual yield is required.
#   - fetch all harvest, deposit, withdrawal events between t0 and t3.
#   - harvest at t2 is responsible for reward distribution within t0 - t2 interval. By calculating
#     strategy balance changes within t0 - t2 we can accurately assign rewards harvested at t2 to any
#     sub interval within t0 - t2. Do the calculation and assign t1 - t2 portion of the rewards to 
#     the daily yield. This part of the yield is exact
#   - since there is no harvest after t3 we need to estimate the rewards for the t2 - t3 interval portion
#     of the calculation:
#        - part of some strategies can still be exactly calculated here: Aave & Compound yield originating
#          from aTokens & cTokens
#        - part of the yield that will come from a future harvest is estimated using the current price of
#          reward tokens. While we can accurately calculate how much reward tokens have been yield farmed
#          we can not know the future price at harvest time when strategy is going to collect the rewards.
#          For that reason this part of the yield is estimated, making the whole t1 - t3 interval be 
#          categorized as an estimated yield interval.

def get_relevant_logs(start_day_block, end_day_block, strategy_address):
    logs_query = Q(topic_0=STRATEGY_REWARD_TOKEN_COLLECTED_TOPIC.lower()) & Q(address=strategy_address.lower())
    logs_query_first_past_harvest = logs_query & Q(block_number__lt=start_day_block)
    logs_query_first_future_harvest = logs_query & Q(block_number__gt=end_day_block)
    
    pastHarvest = Log.objects.filter(logs_query_first_past_harvest).order_by('-block_number').first()
    futureHarvest = Log.objects.filter(logs_query_first_future_harvest).order_by('block_number').first()

    start_block = start_day_block
    end_block = end_day_block
    if pastHarvest is not None:
        start_block = pastHarvest.block_number
    if futureHarvest is not None:
        end_block = futureHarvest.block_number

    return load_logs(start_block, end_block, strategy_address)


def load_logs(start_block, end_block, strategy_address):
    logs_query = Q(block_number__gte=start_block) & Q(block_number__lte=end_block)
    logs_query &= (Q(topic_0=STRATEGY_REWARD_TOKEN_COLLECTED_TOPIC.lower()) | Q(topic_0=STRATEGY_WITHDRAWAL_TOPIC.lower()) | Q(topic_0=STRATEGY_DEPOSIT_TOPIC.lower()))
    logs_query &= Q(address=strategy_address.lower())
    return Log.objects.filter(logs_query)
