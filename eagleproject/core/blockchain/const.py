from decimal import Decimal
from datetime import (
    datetime,
)
from core.blockchain.addresses import (
    AAVE_LENDING_POOL_CORE_V1,
    AAVE_LENDING_POOL_V1,
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
    OGN_STAKING,
    STORY_STAKING_VAULT,
    STORY_STAKING_SEASONS,
    STORY_STAKING_SERIES,
    OUSD,
    OUSD_USDT_UNISWAP,
    STRATAAVEDAI,
    STRATCOMP,
    STRAT3POOL,
    TIMELOCK,
    USDT,
    USDC,
    VAULT,
)

START_OF_EVERYTHING = 10884500
START_OF_EVERYTHING_TIME = datetime.strptime("18-9-2020", "%d-%m-%Y")
# TODO: this might need adjusting
START_OF_CURVE_CAMPAIGN_TIME = datetime.strptime("11-11-2021", "%d-%m-%Y")
START_OF_OUSD_V2 = 11596940
START_OF_OUSD_V2_TIME = datetime.strptime("29-12-2020", "%d-%m-%Y")

CONTRACT_FOR_SYMBOL = {
    "DAI": DAI,
    "USDT": USDT,
    "USDC": USDC,
    "COMP": COMP,
    "ETH": "0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee",
}
SYMBOL_FOR_CONTRACT = {v: k for (k, v) in CONTRACT_FOR_SYMBOL.items()}

DECIMALS_FOR_SYMBOL = {
    "AAVE": 18,
    "COMP": 18,
    "CRV": 18,
    "DAI": 18,
    "LINK": 18,
    "OUSD": 18,
    "USDT": 6,
    "USDC": 6,
    "veCRV": 18,
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
    VAULT,
    STRATCOMP,
    STRATAAVEDAI,
    STRAT3POOL,
    TIMELOCK,
]

LOG_CONTRACTS = (
    OUSD_CONTRACTS
    + STORY_STAKING_SEASONS
    + [
        OUSD_USDT_UNISWAP,
        OGN_STAKING,
        STORY_STAKING_VAULT,
        STORY_STAKING_SERIES,
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
)
ETHERSCAN_CONTRACTS = [
    OUSD,
    GOVERNOR,
    GOVERNORV2,
    GOVERNORV3,
    VAULT,
    TIMELOCK,
    STORY_STAKING_VAULT,
    STORY_STAKING_SERIES,
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
    "apy": "Apy",
    "accounts_analyzed": "Accounts processed",
    "accounts_holding_ousd": "Accounts holding OUSD",
    "accounts_holding_more_than_100_ousd": "Accounts holding over 100 OUSD",
    "new_accounts": "New (first time seen) accounts",
    "accounts_with_non_rebase_balance_increase": "Accounts with balance increased",
    "accounts_with_non_rebase_balance_decrease": "Accounts with balance decreased",
}

curve_report_stats = {
    "accounts_holding_more_than_100_ousd_after_curve_start": "Accounts holding over 100 OUSD after campaign start",
    "new_accounts_after_curve_start": "New accounts after campaign start",
    "curve_metapool_total_supply": "Curve pool supply",
    "share_earning_curve_ogn": "Share earning OGN",
}
