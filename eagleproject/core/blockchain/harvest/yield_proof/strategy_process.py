from decimal import Decimal
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

from core.templatetags.blockchain import (
    EVENT_NAMES
)

from datetime import ( datetime, timedelta, timezone )

from core.blockchain.harvest.blocks import (
    ensure_day,
)

from core.blockchain.rpc import (
    latest_block,
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
    YIELD_UNIT_REASON_LOGS_OPTION_END
)

# TODO: remove
token_balance_cache = {
    0: [Decimal('911_267.337728'), Decimal('1_049_311.747656'), Decimal('864_561.454497888872632797')],
    1: [Decimal('11_406_453.984592'), Decimal('4_320_758.494423'), Decimal('732.755576785005363906')],
    2: [Decimal('4_908_258.970037'), Decimal('1_322_108.028627'), Decimal('732.859382098336821929')],
    3: [Decimal('4_359_788.833714'), Decimal('1_322_855.168741'), Decimal('3_800_733.043666619403158576')],
    4: [Decimal('4_359_906.175533'), Decimal('1_322_906.481429'), Decimal('3_800_812.091266134161563937')],
    5: [Decimal('4_359_942.453749'), Decimal('1_322_921.566498'), Decimal('3_800_836.30961475086546941')],
    6: [Decimal('4_360_123.013314'), Decimal('1_322_997.507131'), Decimal('3_800_959.008187685960286518')],
    7: [Decimal('1_561_039.89638'), Decimal('4_123_537.048162'), Decimal('1_566_685.216107667421881155')],
    8: [Decimal('3_592_000.097296'), Decimal('4_125_204.843341'), Decimal('1_567_083.328943436448118717')],
}

def create_yield_strategy(name, strategy_address, asset_name_list, day, project):

    bare_yield_units: YieldUnitList = build_yield_units(day, strategy_address, asset_name_list, project=project)
    yield_units_with_reward = bare_yield_units.to_yield_units_with_reward()

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
def build_yield_units(day, strategy_address, asset_name_list, project) -> YieldUnitList:
    start_day_block, end_day_block = __get_day_block_range(day)

    # these are all the relevant logs. Potentially even before start block and after
    # end block. Each of these logs is a breaking point that ends one yield unit and
    # starts another.
    logs = get_relevant_logs(start_day_block, end_day_block, strategy_address)
    
    for i in range(len(logs)):
        print(EVENT_NAMES.get(logs[i].topic_0))
        print("\n")

    # The boundaries for each yield unit in block numbers. 
    blocks = [start_day_block, end_day_block]
    all_blocks = list(np.unique(list(map(lambda log: log.block_number, logs)))) + blocks
    all_blocks.sort()
    
    start_reasons = __build_start_reason_dict(logs, blocks)      

    yield_units = []
    for index, block_number in enumerate(all_blocks):
        print(index + 1, "/", len(all_blocks))
        # last block_number in all_blocks is the end interval of previous for loop
        # created BareYieldUnit

        token_balances = []
        for index_inner, asset_name in enumerate(asset_name_list):
            asset_address = CONTRACT_FOR_SYMBOL[asset_name]
            decimals = DECIMALS_FOR_SYMBOL[asset_name]
            # balance = checkBalance(strategy_address, asset_address, decimals, block_number)
            token_balances.append(TokenBalance(asset_address, token_balance_cache[index][index_inner])
            # balance
            )
        print(list(map(lambda a: a.balance, token_balances)))

        # I don't believe this is quite true... seeing some blocks with, for example, 3 withdraw logs when all 3 tokens are being withdrawn from Morpho Compound strategy.
        reasons_info = start_reasons[block_number]
        # if (len(reasons_info) > 1):
        #     # reward token harvest can instantiate multiple logs, that is acceptable
        #     if not all(map(lambda reason_info: reason_info['reason'] == YIELD_UNIT_REASON_REWARD_TOKEN_HARVEST, reasons_info)):
        #         raise Exception("Unexpected reason length: {} block_number: {} strategy_address: {} reasons_info: {}".format(len(reasons_info), block_number, strategy_address, reasons_info))

        # the [index + 1] is to fetch the next block in the list. -1 to set end block number
        # of this yield unit to 1 less than the stating block number of the next yield unit
        curr_yield_unit = BareYieldUnit(
            token_balances,
            block_number,
            all_blocks[index + 1] - 1 if index + 1 < len(all_blocks) else YIELD_UNIT_REASON_LOGS_OPTION_END,
            strategy_address,
            list(map(lambda reason_info: reason_info['reason'], reasons_info)),
            list(map(lambda reason_info: reason_info['log'], reasons_info))
        )

        yield_units.append(
            curr_yield_unit
        )
    return YieldUnitList(yield_units, project=project)


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