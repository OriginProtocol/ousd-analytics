import math
from decimal import Decimal
from core.blockchain.const import (
    YIELD_UNIT_REASON_REWARD_TOKEN_HARVEST,
    STRATEGY_REWARD_TOKEN_COLLECTED_TOPIC,
    YIELD_UNIT_REASON_LOGS_OPTION_END,
    TOKENS_SWAPPED_ON_UNISWAP_V2,
    SYMBOL_FOR_CONTRACT,
    CONTRACT_FOR_SYMBOL,
    SUSHI_POOL_TO_TOKEN,
    SUSHI_REWARD_TOKEN_POOLS,
    SUSHISWAP_USDT_WETH_POOL,
    DECIMALS_FOR_SYMBOL
)

from core.blockchain.harvest.transactions import (
    decode_reward_token_collected_log,
    decode_reward_token_swap_log
)
from core.models import OriginTokens

# yield units represent a sub interval of the strategy's larger yield interval. Strategies when earning
# yield can have: variable APY, variable balance, and different yield types (estimated vs actual). Yield 
# unit has a constant balance, APY and yield type.
#
# See example of this strategy yield interval (y axis is strategy balance, x axis is time):
#
#  ↑
#  |
#  |
#  |
#  |           __________________
#  |           |                |
#  |           |                |
#  |  _________|                |
#  |  |                         |____________...
#  |__|
#  |
#  |--t0-------t1---------t2----t3---t4--------→
#
#
#  Events in the graph: 
#   - t0 deposit increases strategy balance
#   - t1 deposit increases strategy balance
#   - t2 strategy gets harvested -> for demonstration purposes this is the most recent
#        harvest event of above strategy
#   - t3 withdrawal decreases strategy balance
#   - t4 a new day has started (that is UTC+7 by our definition)
#
# Above strategy life cycle would produce the following yield units: 
#   - t0 -> t1 unit with actual yield
#   - t1 -> t2 unit with actual yield
#   - t2 -> t3 unit with estimated yield
#   - t3 -> t4 unit with estimated yield

# Glossary:
#  - Actual yield: yield that is calculated off of reward token harvest transaction
#  - Estimated yield: yield that has not yet been realized and is only estimated. Once the strategy
#    is harvested the actual yield can differ from the estimated one.


class YieldSourceInterface:
    def yield_in_dollars():
        pass

# when price increase is responsible for the yield e.g. curve virtual price increase,
# Aave tokens (aTokens) price increase, ...
class PriceIncreaseYieldSource(YieldSourceInterface):
    def __init__(self, token, amount, priceBefore, priceAfter):
        self.token = token
        # amount already denominated token's decimals
        self.amount = amount
        self.priceBefore = priceBefore
        self.priceAfter = priceAfter

    def yield_in_dollars():
        return self.amount * (self.priceBefore - self.priceAfter)

# when more tokens are handed out for the yield e.g. Curve, Convex rewards, Compound tokens...
class TokensIncreaseYieldSource(YieldSourceInterface):
    def __init__(self, token, amount, price):
        self.token = token
        # amount already denominated token's decimals
        self.amount = amount
        self.price = price

    def yield_in_dollars():
        return self.amount * self.price

class TokenBalance:
    def __init__(self, token_address, balance):
        self.token_address = token_address
        self.balance = balance
        self.symbol = SYMBOL_FOR_CONTRACT[token_address]

    def __str__(self):
        return 'TokenBalance: balance: {} address: {}'.format(self.balance, self.token_address)


# param price: price of reward token denominated in decimals of the rewards token. e.g. USDT ~= 1
class TokenBalanceWithPrice:
    def __init__(self, token_address, balance, price):
        TokenBalance.__init__(self, token_address, balance)
        self.price = price

    def __str__(self):
        return 'TokenBalanceWithPrice: balance: {} address: {} price: {}'.format(self.balance, self.token_address, self.price)


# an interval with constant balances
# param reason -> the start reason for this yield unit
# param reasonLogsOption -> optional log(s) event that is(are) the cause to start this yield unit
#       ReardTokenCollected logs also have swap logs accompanying them so we can figure out the 
#       tokens sold price.
class BareYieldUnit:
    def __init__(
        self,
        token_balances,
        from_block,
        to_block,
        strategy_address,
        reason,
        reason_logs_option
    ):
        # balance of each of the assets -> array of TokenBalance
        self.token_balances = token_balances
        self.from_block = from_block
        self.to_block = to_block
        self.strategy_address = strategy_address
        self.reason = reason
        self.reason_logs_option = reason_logs_option

    def __str__(self):
        return 'BareYieldUnit: from_block: {} to_block: {} strategy_address: {} reason: {} reason_logs_option: {} token_balances: {}'.format(self.from_block, self.to_block, self.strategy_address, self.reason, list(map(lambda x: str(x), self.reason_logs_option)), list(map(lambda x: str(x), self.token_balances)))

    def block_range(self):
        return self.to_block - self.from_block

# an interval with constant balances and accompanying rewards
# param baseReward: dollar amount of rewards gained due to LP token value accrue-al (cTokens, aToken, Convex LP tokens)
# param rewardTokenBalances: reward token balances with price of this yield unit
# param is_estimated: if true then prices in reward token balances are actual prices at which the protocol
#                     has sold the reward tokens for. If false the prices are current and might change until 
#                     the rewards are harvested and reward tokens sold.
class YieldUnitWithReward(BareYieldUnit):
    def __init__(
        self,
        token_balances,
        from_block,
        to_block,
        strategy_address,
        reason,
        reason_logs_option,
        base_reward,
        reward_token_balances,
        is_estimated
    ):
        BareYieldUnit.__init__(self, token_balances, from_block, to_block, strategy_address, reason, reason_logs_option)
        self.base_reward = base_reward
        self.reward_token_balances = reward_token_balances
        self.is_estimated = is_estimated



class YieldUnitList:
    def __init__(self, yield_units, project, reward_balances=False):
        self.yield_units = yield_units
        sorted(self.yield_units, key=lambda yu: yu.from_block)
        self.project = project
        self.reward_balances_per_asset = {}

        # if reward balances are passed to constructor of a yield unit, according to the 
        # weighted balance of assets in the strategy the reward token shall be split up
        # between those assets
        if reward_balances != False:
            average_token_balances, average_total, total_block_range = self.average_token_balances()
            self.reward_balances_per_asset = {}
            for reward_balance in reward_balances:
                for average_token_balance_address in average_token_balances.keys():
                    average_token_balance_symbol = SYMBOL_FOR_CONTRACT[average_token_balance_address]

                    if reward_balance.symbol not in self.reward_balances_per_asset:
                        self.reward_balances_per_asset[reward_balance.symbol] = {}

                    # Share of the reward token that can be attributed to a single asset
                    reward_token_amount = average_token_balances[average_token_balance_address] / average_total * reward_balance.balance
                    self.reward_balances_per_asset[reward_balance.symbol][average_token_balance_symbol] = TokenBalanceWithPrice(reward_balance.token_address, reward_token_amount, reward_balance.price)


    # in order to be able to break down harvest rewards to separate yield units we need the
    # context of all the yield units that are responsible for said harvest event.
    def generate_yield_units_with_rewards(self):
        if type(self.reward_balances_per_asset) is not dict:
            raise Exception("reward_balances missing from this Yield Unit List")

        average_token_balances, average_total, total_block_range = self.average_token_balances()
        yield_units_with_reward = []
        # multiply rewards with this factor to get amount of reward $1 unit of liquidity
        # earns per 1 block
        yield_per_block_per_unit_of_asset_rate = 0 if average_total == 0 or total_block_range == 0 else 1 / average_total / total_block_range

        for yield_unit in self.yield_units:
            reward_token_balances = {}
            for token_balance in yield_unit.token_balances:
                if token_balance.token_address not in reward_token_balances:
                    reward_token_balances[token_balance.token_address] = {}

                for reward_token_symbol in self.reward_balances_per_asset.keys():
                    yield_unit_list_reward = self.reward_balances_per_asset[reward_token_symbol]
                    reward_token_address = CONTRACT_FOR_SYMBOL[reward_token_symbol]

                    reward_token_balances[token_balance.token_address][reward_token_address] = TokenBalanceWithPrice(
                        yield_unit_list_reward[token_balance.symbol].token_address,
                        yield_unit_list_reward[token_balance.symbol].balance * yield_per_block_per_unit_of_asset_rate * yield_unit.block_range() * token_balance.balance,
                        yield_unit_list_reward[token_balance.symbol].price
                    )

            # use yield_unit.strategy_address to get to base reward do it as a function                    

            yield_units_with_reward.append(YieldUnitWithReward(
                yield_unit.token_balances,
                yield_unit.from_block,
                yield_unit.to_block,
                yield_unit.strategy_address,
                yield_unit.reason,
                yield_unit.reason_logs_option,
                # TODO need to calculate base reward
                False, #base_reward,
                reward_token_balances,
                False #is_estimated
            ))

        return yield_units_with_reward





    # average token balance of every asset per block for the whole list of yield units. 
    # Denominated in token's decimals. Second return value in the list is total average
    # token balances which is the aggregate of all the average token balances. Third property
    # is total block range of the yieldUnitList
    def average_token_balances(self):
        yield_units = self.yield_units

        # sanity checks
        if (len(yield_units) < 1):
            raise Exception("YieldUnitList has no yield units")
        if (yield_units[0].reason[0] != YIELD_UNIT_REASON_REWARD_TOKEN_HARVEST):
            raise Exception("YieldUnitList does not start with a reward token harvest")
        
        # if the last yield unit is not a reward token harvest, it must mean we are on the most recent (today) yield unit. So it must have a reason of end logs option
        if (yield_units[-1].reason[0] != YIELD_UNIT_REASON_REWARD_TOKEN_HARVEST and yield_units[-1].reason[1] != YIELD_UNIT_REASON_LOGS_OPTION_END):
            raise Exception("YieldUnitList does not end with a reward token harvest or with end logs option")

        aggregator = {}
        total_block_range = 0
        for yield_unit in self.yield_units:
            total_block_range += yield_unit.block_range()

            for token_balance in yield_unit.token_balances:
                if token_balance.token_address not in aggregator:
                    aggregator[token_balance.token_address] = 0
                aggregator[token_balance.token_address] += yield_unit.block_range() * token_balance.balance

        total = 0        
        for asset_address in aggregator.keys():
            average_asset_balance = aggregator[asset_address] / total_block_range
            total += average_asset_balance
            aggregator[asset_address] = average_asset_balance

        
        # average token balances, total token balances
        return [aggregator, total, total_block_range]


    def __str__(self):
        return 'YieldUnitList: {} reward_tokens: {}'.format(list(map(lambda x: str(x), self.yield_units)), self.reward_balances_per_asset)


    def to_yield_units_with_reward(self):
        def convert_to_reward_yield_units_with_harvest(units_to_be_converted, yield_unit):
            harvest_logs = list(map(
                lambda log: decode_reward_token_collected_log(log), 
                filter(
                    lambda log: log.topic_0 == STRATEGY_REWARD_TOKEN_COLLECTED_TOPIC,
                    yield_unit.reason_logs_option
                )
            ))
            swap_logs = list(map(
                lambda log: decode_reward_token_swap_log(log), 
                filter(
                    lambda log: log.topic_0 == TOKENS_SWAPPED_ON_UNISWAP_V2,
                    yield_unit.reason_logs_option
                )
            ))
            # Price of reward tokens in USDT for OUSD and WETH for OETH
            token_prices = self.__get_USDT_token_price_from_swap_log(swap_logs)

            # convert harvest logs to token balances with price
            reward_token_balances = []
            for harvest_log in harvest_logs:
                reward_token_symbol = SYMBOL_FOR_CONTRACT[harvest_log['rewardToken']]
                reward_token_decimals = DECIMALS_FOR_SYMBOL[reward_token_symbol]
                reward_token_balances.append(TokenBalanceWithPrice(
                    harvest_log['rewardToken'],
                    harvest_log['amount'] / Decimal(math.pow(10, reward_token_decimals)),
                    token_prices[reward_token_symbol] if reward_token_symbol in token_prices else 0
                ))
            
            # these are all yield units tied to a single harvest event. There
            # will be one harvest event at the beginning and one at the end to
            # fully show all the divisions between yield events
            unit_list_with_single_harvest = YieldUnitList(units_to_be_converted, self.project, reward_token_balances)
            reward_yield_units = unit_list_with_single_harvest.generate_yield_units_with_rewards()
            return reward_yield_units


        ###### MAIN to_yield_units_with_reward ####### 
        units_to_be_converted = []
        final_yield_units = []
        for index, yield_unit in enumerate(self.yield_units):
            units_to_be_converted.append(yield_unit)

            # Harvest event found, calculate exact - non estimated rewards for yield units
            if  YIELD_UNIT_REASON_REWARD_TOKEN_HARVEST in yield_unit.reason:
                # harvest events apply to yield units in the past. If non in the array
                # can not really apply them, so continue
                if len(units_to_be_converted) == 1:
                    continue
            
                # Once we find a harvest event (that is not the first), we want to distribute the yield to the past yield units.
                yield_units_with_reward = convert_to_reward_yield_units_with_harvest(units_to_be_converted, yield_unit)
                final_yield_units += yield_units_with_reward

                units_to_be_converted = []

        # final yield unit is not harvest event
        if len(units_to_be_converted) > 0:
            #units_to_be_converted -> turn into estimated units and add to final_yield_units
            pass


    def __get_USDT_token_price_from_swap_log(self, swap_logs):
        token_prices = {}
        for swap_log in swap_logs:
            if swap_log['pool'] in SUSHI_REWARD_TOKEN_POOLS:
                reward_token = SUSHI_POOL_TO_TOKEN[swap_log['pool']]
                reward_token_amount = swap_log['amount0In'] + swap_log['amount1In']
                # For OUSD
                # since SUSHI pool swaps are done via: 
                # reward token -> WETH -> USDT
                # besides reward token swap (swapping reward token to WETH)
                # there should be one more corresponding swap
                # swapping it to USDT

                # when swapping reward token for WETH the WETH is the amount
                # out whether it is first or second token in the pool
                weth_total = swap_log['amount0Out'] + swap_log['amount1Out']
                # find corresponding USDT log match
                for swap_log in swap_logs:
                    if self.project == OriginTokens.OUSD:
                        if swap_log['amount0In'] == weth_total | swap_log['amount1In'] == weth_total:
                            if swap_log['pool'] != SUSHISWAP_USDT_WETH_POOL:
                                raise Exception("Expected corresponding swap log to be on USDT pool rather got: {}".format(swap_log['pool']))
                            reward_token_symbol = SYMBOL_FOR_CONTRACT[reward_token]
                            reward_token_decimals = DECIMALS_FOR_SYMBOL[reward_token_symbol]
                            usdt_out = swap_log['amount0Out'] + swap_log['amount1Out']

                            reward_token_amount_normalized = reward_token_amount / Decimal(math.pow(10, reward_token_decimals))
                            usdt_normalized = usdt_out / Decimal(math.pow(10, 6))
                            token_prices[reward_token_symbol] = usdt_normalized / reward_token_amount_normalized
                    else:
                        reward_token_symbol = SYMBOL_FOR_CONTRACT[reward_token]
                        reward_token_decimals = DECIMALS_FOR_SYMBOL[reward_token_symbol]

                        reward_token_amount_normalized = reward_token_amount / Decimal(math.pow(10, reward_token_decimals))
                        weth_normalized = weth_total / Decimal(math.pow(10, 18))
                        token_prices[reward_token_symbol] = weth_normalized / reward_token_amount_normalized 

        return token_prices
                            

class YieldUnitWithRewardsList(YieldUnitList):
    def __init__(self, yield_units):
        YieldUnitList.__init__(self, yield_units)



# includes yield sources
class YieldUnitWithRewards(BareYieldUnit):
    def __init__(self, token_balances, from_block, to_block, is_actual, yield_sources):
        base.__init__(token_balances, from_block, to_block)
        # if true -> actual yield if false -> estimated yield. See top of this file for
        # further info on the terms
        self.is_actual = is_actual
        self.yield_sources = yield_sources

class BaseStrategyYield:
    def __init__(self, name, strategy_address, start_day_block, end_day_block):
        self.name = name
        self.start_day_block = start_day_block
        self.end_day_block = end_day_block
        self.strategy_address = strategy_address

    def __str__(self):
        return 'base strategy: name: {} start_day_block: {} end_day_block: {} strategy_address:{}'.format(self.name, self.start_day_block, self.end_day_block, self.strategy_address)
