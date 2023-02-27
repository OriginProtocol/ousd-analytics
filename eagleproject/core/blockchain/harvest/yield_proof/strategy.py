from core.blockchain.const import (
    YIELD_UNIT_REASON_REWARD_TOKEN_HARVEST,
    STRATEGY_REWARD_TOKEN_COLLECTED_TOPIC,
    SYMBOL_FOR_CONTRACT
)

from core.blockchain.harvest.transactions import (
    decode_reward_token_collected_log
)

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
class BareYieldUnit:
    def __init__(
        self,
        token_balances,
        from_block,
        to_block,
        reason,
        reason_logs_option
    ):
        # balance of each of the assets
        self.token_balances = token_balances
        self.from_block = from_block
        self.to_block = to_block
        self.reason = reason
        self.reason_logs_option = reason_logs_option

    def __str__(self):
        return 'BareYieldUnit: from_block: {} to_block: {} reason: {} reason_logs_option: {} token_balances: {}'.format(self.from_block, self.to_block, self.reason, list(map(lambda x: str(x), self.reason_logs_option)), list(map(lambda x: str(x), self.token_balances)))

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
        reason,
        reason_logs_option,
        base_reward,
        reward_token_balances,
        is_estimated
    ):
        BareYieldUnit.__init__(self, token_balances, from_block, to_block, reason, reason_logs_option)
        self.base_reward = base_reward
        self.reward_token_balances = reward_token_balances
        self.is_estimated = is_estimated



class YieldUnitList:
    def __init__(self, yield_units):
        self.yield_units = yield_units
        sorted(self.yield_units, key=lambda yu: yu.from_block)

    # average token balance per block for the whole list or yield units
    def average_token_balances(self):
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

        
        return [aggregator, total]


    def __str__(self):
        return 'YieldUnitList: {}'.format(list(map(lambda x: str(x), self.yield_units)))


    def to_yield_units_with_reward(self):
        units_to_be_converted = []
        for index, yield_unit in enumerate(self.yield_units):
            # Harvest event found, calculate exact - non estimated rewards for yield units
            if yield_unit.reason == YIELD_UNIT_REASON_REWARD_TOKEN_HARVEST:
                # harvest events apply to yield units in the past. If non in the array
                # can not really apply them, so continue
                if len(units_to_be_converted) == 0:
                    continue
            
                harvest_logs = list(map(
                    lambda log: decode_reward_token_collected_log(log), 
                    filter(
                        lambda log: log.topic_0 == STRATEGY_REWARD_TOKEN_COLLECTED_TOPIC,
                        yield_unit.reason_logs_option
                    )
                ))
                #1. for each token reward get price
                #2. create token balance with price
                #3. split it up to each yield unit

                print("harvest_logs", harvest_logs)
                #units_to_be_converted    

            # we have reached the final yield unit without a harvest event. Estimate the
            # yield for all yield units in units_to_be_converted
            if (index == len(self.yield_units) - 1):
                pass

            units_to_be_converted.append(yield_unit)


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



