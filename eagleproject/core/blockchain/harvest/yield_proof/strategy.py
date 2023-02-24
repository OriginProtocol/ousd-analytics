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

# just an interval with constant balances
class BareYieldUnit:
    def __init__(self, token_balances, from_block, to_block):
        # balance of each of the assets
        self.token_balances = token_balances
        self.from_block = from_block
        self.to_block = to_block

    def __str__(self):
        return 'BareYieldUnit: from_block: {} to_block: {} token_balances: {}'.format(self.from_block, self.to_block, list(map(lambda x: str(x), self.token_balances)))

    def block_range(self):
        return self.to_block - self.from_block

class YieldUnitList:
    def __init__(self, yield_units):
        self.yield_units = yield_units

    # average token balance per block for the whole list
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
            print("xxxxx", aggregator[asset_address], total_block_range)
            average_asset_balance = aggregator[asset_address] / total_block_range
            total += average_asset_balance
            aggregator[asset_address] = average_asset_balance

        
        return [aggregator, total]


    def __str__(self):
        return 'YieldUnitList: {}'.format(list(map(lambda x: str(x), self.yield_units)))


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



