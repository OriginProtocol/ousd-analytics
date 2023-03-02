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
    TOKENS_SWAPPED_ON_UNISWAP_V2,
    CONTRACT_FOR_SYMBOL,
    DECIMALS_FOR_SYMBOL,
    YIELD_UNIT_REASON_REWARD_TOKEN_HARVEST,
    YIELD_UNIT_REASON_DEPOSIT,
    YIELD_UNIT_REASON_WITHDRAWAL,
    YIELD_UNIT_REASON_CUSTOM_BLOCK_BREAK,
)

def create_yield_strategy(name, strategy_address, asset_name_list, start_day_block, end_day_block):
    # these are all the relevant logs. Potentially even before start block and after
    # end block. Each of these logs is a breaking point that ends one yield unit and
    # starts another.
    logs = get_relevant_logs(start_day_block, end_day_block, strategy_address)
    bare_yield_units = build_yield_units(logs, [start_day_block, end_day_block], strategy_address, asset_name_list)
    yield_units_with_reward = bare_yield_units.to_yield_units_with_reward()

    #average_token_balances, average_total = bare_yield_units.average_token_balances()
    #print("bare_yield_units", bare_yield_units, average_token_balances, average_total)

    return BaseStrategyYield(name, strategy_address, start_day_block, end_day_block)


def __build_start_reason_dict(logs, blocks):
    start_reasons = {}
    for log in logs:
        if log.block_number not in start_reasons:
            start_reasons[log.block_number] = []

        if log.topic_0 == STRATEGY_REWARD_TOKEN_COLLECTED_TOPIC:
            start_reasons[log.block_number].append({
                "reason": YIELD_UNIT_REASON_REWARD_TOKEN_HARVEST,
                "log": log
            })
        elif log.topic_0 == STRATEGY_DEPOSIT_TOPIC:
            start_reasons[log.block_number].append({
                "reason": YIELD_UNIT_REASON_DEPOSIT,
                "log": log
            })
        elif log.topic_0 == STRATEGY_WITHDRAWAL_TOPIC:
            start_reasons[log.block_number].append({
                "reason": YIELD_UNIT_REASON_WITHDRAWAL,
                "log": log
            })
        elif log.topic_0 == TOKENS_SWAPPED_ON_UNISWAP_V2:
            start_reasons[log.block_number].append({
                "reason": YIELD_UNIT_REASON_REWARD_TOKEN_HARVEST,
                "log": log
            })
        else: 
            raise Exception("Unexpected log topic_0: {}".format(log.topic_0))

    for block in blocks:
        if block not in start_reasons:
            start_reasons[block] = []

        start_reasons[block].append({
            "reason": YIELD_UNIT_REASON_CUSTOM_BLOCK_BREAK,
            "log": False
        })  
    return start_reasons

# create build units out of logs. Blocks play as additional breaking points that split yield
# unit into 2.
def build_yield_units(logs, blocks, strategy_address, asset_name_list):
    all_blocks = list(np.unique(list(map(lambda log: log.block_number, logs)))) + blocks
    all_blocks.sort()
    
    start_reasons = __build_start_reason_dict(logs, blocks)      

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

        reasons_info = start_reasons[block_number]
        if (len(reasons_info) > 1):
            # reward token harvest can instantiate multiple logs, that is acceptable
            if not all(map(lambda reason_info: reason_info['reason'] == YIELD_UNIT_REASON_REWARD_TOKEN_HARVEST, reasons_info)):
                raise Exception("Unexpected reason length: {} block_number: {} strategy_address: {} reasons_info: {}".format(len(reasons_info), block_number, strategy_address, reasons_info))

        # the [index + 1] is to fetch the next block in the list. -1 to set end block number
        # of this yield unit to 1 less than the stating block number of the next yield unit
        yield_units.append(
            BareYieldUnit(
                token_balances,
                block_number,
                all_blocks[index + 1] - 1,
                strategy_address,
                reasons_info[0]['reason'],
                list(map(lambda reason_info: reason_info['log'], reasons_info))
            )
        )
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
    logs_query = Q(topic_0=STRATEGY_REWARD_TOKEN_COLLECTED_TOPIC) & Q(address=strategy_address.lower())
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
    logs_query &= (
        Q(topic_0=STRATEGY_REWARD_TOKEN_COLLECTED_TOPIC) |
        Q(topic_0=STRATEGY_WITHDRAWAL_TOPIC) |
        Q(topic_0=STRATEGY_DEPOSIT_TOPIC)
    )
    logs_query &= Q(address=strategy_address.lower())

    logs = list(Log.objects.filter(logs_query))
    log_block_numbers = list(map(lambda log: log.block_number, logs))
    # swap logs are required to figure out the price for which the tokens were swapped at harvest
    swap_logs = list(Log.objects.filter(
        Q(block_number__in=log_block_numbers) &
        Q(topic_0=TOKENS_SWAPPED_ON_UNISWAP_V2)
    ))

    return logs + swap_logs
