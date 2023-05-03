import os
from decimal import Decimal
from datetime import (
    datetime,
)
from core.blockchain.addresses import (
    AAVE_PROTO_GOVERNANCE_V1,
    CHAINLINK_KEEPER_REGISTRY,
    COMP,
    COMPENSATION_CLAIMS,
    COMPOUND_GOVERNOR_ALPHA,
    COMPOUND_GOVERNOR_BRAVO,
    COMPOUND_TIMELOCK,
    CDAI,
    CUSDC,
    CUSDT,
    CURVE_ARAGON_51,
    CURVE_ARAGON_60,
    DAI,
    GOVERNOR,
    GOVERNORV2,
    GOVERNORV3,
    OGN,
    OGN_STAKING,
    STORY_STAKING_VAULT,
    STORY_STAKING_SEASONS,
    STORY_STAKING_SERIES,
    OUSD,
    OUSD_USDT_UNISWAP,
    LUSD,
    STRATAAVEDAI,
    STRATCOMP,
    STRAT3POOL,
    TIMELOCK,
    USDT,
    USDC,
    OUSD_VAULT,
    GOVERNANCE,
    GOVERNANCE_TIMELOCK,
    OGV_BUYBACK,
    THREEPOOL,
    OETH_VAULT,
    OETH,
    FRXETH,
    RETH,
    STETH,
    WETH
)

from core.blockchain.strategies import OUSD_STRATEGIES, OETH_STRATEGIES

START_OF_EVERYTHING = int(os.environ.get("LOCAL_START_OF_EVERYTHING", 10884500))
START_OF_EVERYTHING_TIME = datetime.strptime("18-9-2020", "%d-%m-%Y")
# TODO: this might need adjusting
START_OF_CURVE_CAMPAIGN_TIME = datetime.strptime("11-11-2021", "%d-%m-%Y")
START_OF_OUSD_V2 = 11596940
START_OF_OUSD_V2_TIME = datetime.strptime("29-12-2020", "%d-%m-%Y")
START_OF_OUSD_TOTAL_SUPPLY_UPDATED_HIGHRES=13534392
OUSD_TOTAL_SUPPLY_UPDATED_TOPIC="0x99e56f783b536ffacf422d59183ea321dd80dcd6d23daa13023e8afea38c3df1"
OUSD_TOTAL_SUPPLY_UPDATED_HIGHRES_TOPIC="0x41645eb819d3011b13f97696a8109d14bfcddfaca7d063ec0564d62a3e257235"

START_OF_OETH = 17067000

CONTRACT_FOR_SYMBOL = {
    "OGN": OGN,
    "DAI": DAI,
    "USDT": USDT,
    "USDC": USDC,
    "COMP": COMP,
    "OUSD": OUSD,
    "LUSD": LUSD,
    "3CRV": THREEPOOL,
    "ETH": "0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee",

    "OETH": OETH,
    "WETH": WETH,
    "RETH": RETH,
    "STETH": STETH,
    "FRXETH": FRXETH,

}
SYMBOL_FOR_CONTRACT = {v: k for (k, v) in CONTRACT_FOR_SYMBOL.items()}

DECIMALS_FOR_SYMBOL = {
    "AAVE": 18,
    "COMP": 18,
    "CRV": 18,
    "DAI": 18,
    "LINK": 18,
    "OGN": 18,
    "OGV": 18,
    "OUSD": 18,
    "LUSD": 18,
    "USDT": 6,
    "USDC": 6,
    "veCRV": 18,
    "3CRV": 18,

    "OETH": 18,
    "WETH": 18,
    "RETH": 18,
    "STETH": 18,
    "FRXETH": 18,
    "SFRXETH": 18,
}

THREEPOOLINDEX_FOR_ASSET = {
    DAI: 0,
    USDC: 1,
    USDT: 2,
}

COMPOUND_FOR_SYMBOL = {
    "DAI": CDAI,
    "USDT": CUSDT,
    "USDC": CUSDC,
}
SYMBOL_FOR_COMPOUND = {v: k for (k, v) in COMPOUND_FOR_SYMBOL.items()}

CTOKEN_DECIMALS = 8

OUSD_CONTRACTS = [
    GOVERNOR,
    GOVERNORV2,
    GOVERNORV3,
    OUSD,
    OUSD_VAULT,
    GOVERNANCE,
    GOVERNANCE_TIMELOCK,
    STRATCOMP,
    STRATAAVEDAI,
    STRAT3POOL,
    TIMELOCK,
]

OETH_CONTRACTS = [
    OETH_VAULT,
]

OTHER_OUSD_STRAT_CONTRACTS = [strat["ADDRESS"] for (_, strat) in OUSD_STRATEGIES.items() if strat.get("HARDCODED", False) == False]
OETH_STRAT_CONTRACTS = [strat["ADDRESS"] for (_, strat) in OETH_STRATEGIES.items()]

LOG_CONTRACTS = (
    OUSD_CONTRACTS
    + STORY_STAKING_SEASONS
    + [
        OUSD_USDT_UNISWAP,
        OGN_STAKING,
        STORY_STAKING_VAULT,
        STORY_STAKING_SERIES,
        OGV_BUYBACK,
    ]
    + OTHER_OUSD_STRAT_CONTRACTS
    + OETH_CONTRACTS
    + OETH_STRAT_CONTRACTS
)

# Skip log fetching for these contracts if SKIP_THIRD_PARTY is set to "true"
if os.environ.get("SKIP_THIRD_PARTY") != "true":
    LOG_CONTRACTS += [
        COMPOUND_GOVERNOR_ALPHA,
        COMPOUND_GOVERNOR_BRAVO,
        COMPOUND_TIMELOCK,
        COMPENSATION_CLAIMS,
        # TODO
        # AAVE_LENDING_POOL_CORE_V1,
        # AAVE_LENDING_POOL_V1,
        AAVE_PROTO_GOVERNANCE_V1,
        CURVE_ARAGON_51,
        CURVE_ARAGON_60,
        CHAINLINK_KEEPER_REGISTRY,
    ]

ETHERSCAN_CONTRACTS = [
    OUSD,
    GOVERNOR,
    GOVERNORV2,
    GOVERNORV3,
    OUSD_VAULT,
    TIMELOCK,
    GOVERNANCE,
    GOVERNANCE_TIMELOCK,
    STORY_STAKING_VAULT,
    STORY_STAKING_SERIES,
    OGV_BUYBACK,
    OETH
]

ASSET_TICKERS = ["DAI", "USDC", "USDT"]
AAVE_ASSETS = ["DAI"]
OUSD_KEEPER_UPKEEP_ID = 71

BLOCKS_PER_MINUTE = 4
BLOCKS_PER_HOUR = BLOCKS_PER_MINUTE * 60
BLOCKS_PER_DAY = 6400
BLOCKS_PER_YEAR = BLOCKS_PER_DAY * 365

E_6 = Decimal(1e6)
E_8 = Decimal(1e8)
E_18 = Decimal(1e18)
E_27 = Decimal(1e27)

FALSE_256BIT = (
    "0x0000000000000000000000000000000000000000000000000000000000000000"
)
TRUE_256BIT = (
    "0x0000000000000000000000000000000000000000000000000000000000000001"
)

report_stats = {
    "fees_generated": "Fees generated",
    "accounts_holding_more_than_100_ousd": "Accounts holding over 100 OUSD",
    "curve_supply": "Curve pool supply",
    "average_ousd_volume": "Average daily trading volume"
}

curve_report_stats = {
    "accounts_holding_more_than_100_ousd_after_curve_start": "Accounts holding over 100 OUSD after campaign start",
    "new_accounts_after_curve_start": "New accounts after campaign start",
    "curve_metapool_total_supply": "Curve pool supply",
    "share_earning_curve_ogn": "Share earning OGN",
}
