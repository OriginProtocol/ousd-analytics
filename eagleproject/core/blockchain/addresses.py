"""
Addresses we should know about, including mappings from address to name.

Notes
-----
- Addresses in this codebase are all lowercase.
"""
ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"

# Assets
USDT = "0xdac17f958d2ee523a2206206994597c13d831ec7"
USDC = "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48"
DAI = "0x6b175474e89094c44da98b954eedeac495271d0f"
COMP = "0xc00e94cb662c3520282e6f5717214004a7f26888"
CDAI = "0x5d3a536e4d6dbd6114cc1ead35777bab948e3643"
CUSDC = "0x39aa39c021dfbae8fac545936693ac917d5e7563"
CUSDT = "0xf650c3d88d12db855b8bf7d11be6c55a4e07dcc9"
ADAI_V1 = "0xfc1e690f61efd961294b3e1ce3313fbd8aa4f85d"
ADAI_V2 = "0x028171bca77440897b824ca71d1c56cac55b68a3"
AUSDC = "0xbcca60bb61934080951369a648fb03df4f96263c"
AUSDT = "0x3ed3b47dd13ec9a98b44e6204a523e766b225811"
LINK = "0x514910771af9ca656af840dff83e8264ecf986ca"

THREEPOOL = "0x6c3f90f043a72fa612cbac8115ee7e52bde6e490"

# OUSD
GOVERNOR = "0x8e7bdfecd1164c46ad51b58e49a611f954d23377"
GOVERNORV2 = "0x830622bdd79cc677ee6594e20bbda5b26568b781"
GOVERNORV3 = "0x72426ba137dec62657306b12b1e869d43fec6ec7"
OUSD = "0x2a8e1e676ec238d8a992307b495b45b3feaa5e86"
VAULT = "0xe75d77b1865ae93c7eaa3040b038d7aa7bc02f70"
TIMELOCK = "0x52bebd3d7f37ec4284853fd5861ae71253a7f428"
COMPENSATION_CLAIMS = "0x9c94df9d594ba1eb94430c006c269c314b1a8281"

# OGN
OGN = "0x8207c1ffc5b6804f6024322ccf34f29c3541ae26"
OGN_STAKING = "0x501804b374ef06fa9c427476147ac09f1551b9a0"

# Strategies
STRATCOMP1 = "0xd5433168ed0b1f7714819646606db509d9d8ec1f"
STRATCOMP2 = "0x9c459eeb3fa179a40329b81c1635525e9a0ef094"
STRATCOMP = STRATCOMP2
STRATAAVEDAI = "0x9f2b18751376cf6a3432eb158ba5f9b1abd2f7ce"
STRATAAVE2 = "0x5e3646a1db86993f73e6b74a57d8640b69f7e259"
STRATAAVE = STRATAAVE2
STRAT3POOL = "0x3c5fe0a3922777343cbd67d3732fcdc9f2fa6f2f"

OUSD_USDT_UNISWAP = "0xcc01d9d54d06b6a0b6d09a9f79c3a6438e505f71"
OUSD_USDT_SUSHI = "0xe4455fdec181561e9ffe909dde46aaeaedc55283"
SNOWSWAP = "0x7c2fa8c30db09e8b3c147ac67947829447bf07bd"

# Oracles
MIX_ORACLE = "0x4d4f5e7a1fe57f5ceb38bfce8653effa5e584458"  # Meta oracle
OPEN_ORACLE = "0x922018674c12a7f0d394ebeef9b58f186cde13c1"  # Token prices
CHAINLINK_ORACLE = "0x8de3ac42f800a1186b6d70cb91e0d6876cc36759"  # Tokens

CHAINLINK_ETH_USD_FEED = "0x5f4ec3df9cbd43714fe2740f5e3616155c5b8419"  # ETH
CHAINLINK_DAI_ETH_FEED = "0x773616e4d11a78f511299002da57a0a94577f1f4"
CHAINLINK_USDC_ETH_FEED = "0x986b5e1e1755e3c2440e960477f25201b0a8bbd4"
CHAINLINK_USDT_ETH_FEED = "0xee9f2375b4bdf6387aa8265dd4fb8f16512a1d46"

CHAINLINK_KEEPER_REGISTRY = "0x7b3ec232b08bd7b4b3305be0c044d907b2df960b"
# Related, see OUSD_KEEPER_UPKEEP_ID in blockchain.const
OUSD_KEEPER = "0xbc72b4617e8fae53fcf0dd428e16ac5f830c1440"

# Compound
COMPOUND_GOVERNOR_ALPHA = "0xc0da01a04c3f3e0be433606045bb7017a7323e38"
COMPOUND_GOVERNOR_BRAVO = "0xc0da02939e1441f497fd74f78ce7decb17b66529"
COMPOUND_TIMELOCK = "0x6d903f6003cca6255d85cca4d3b5e5146dc33925"

COMPOUND_COMPTROLLER = "0x3d9819210a31b4961b30ef54be2aed79b9c9cd3b"
COMPOUND_COMPTROLLER_G7 = "0xbe7616b06f71e363a310aa8ce8ad99654401ead7"

# Aave v1
AAVE_LENDING_POOL_V1 = "0x398ec7346dcd622edc5ae82352f02be94c62d119"
AAVE_LENDING_POOL_CORE_V1 = "0x3dfd23a6c5e8bbcfc9581d2e864a68feb6a076d3"
AAVE_PROTO_GOVERNANCE_V1 = "0x8a2efd9a790199f4c94c6effe210fce0b4724f52"

# Aave v2
AAVE_LENDING_POOL_V2 = "0x7d2768de32b0b80b7a3454c06bdac94a69ddc7a9"

# Curve
CURVE_CRV_TOKEN = "0xd533a949740bb3306d119cc777fa900ba034cd52"
CURVE_3CRV_TOKEN = "0x6c3f90f043a72fa612cbac8115ee7e52bde6e490"
CURVE_3POOL = "0xbebc44782c7db0a1a60cb6fe97d0b483032ff1c7"
CURVE_ANOTHER_3POOL = "0xa79828df1850e8a3a3064576f380d90aecdd3359"
CURVE_METAPOOL = "0x87650d7bbfc3a9f10587d7778206671719d9910d"
CURVE_METAPOOL_GAUGE = "0x25f0ce4e2f8dba112d9b115710ac297f816087cd"

# Various
METAMASK_SWAP_ROUTER = "0x881d40237659c251811cec9c364ef91dc08d300c"
FLIPPER = "0xcecad69d7d4ed6d52efcfa028af8732f27e08f70"
UNISWAP_V3_ROUTER = "0xe592427a0aece92de3edee1f18e0157c05861564"
OX_EXCHANGE = "0xdef1c0ded9bec7f1a1670819833240f027b25eff"
ONE_INCH_V3 = "0x11111112542d85b3ef69ae05771c2dccff4faa26"
SUSHISWAP = "0xd9e1ce17f2641f24ae83637ab66a2cca9c378b9f"
UNISWAP_V2 = "0x7a250d5630b4cf539739df2c5dacb4c659f2488d"
MISTX_ROUTER = "0xa58f22e0766b3764376c92915ba545d583c19dbc"

# Curve Governance

# This is kinda confusing and I never got an answer from Curve discord but they
# have two voting contracts "installed" in their Aragon DAO app.  They are
# exactly the same (bytecode/source) but have slightly different parameters.

# This contract needs 51% support to pass
CURVE_ARAGON_51 = "0xe478de485ad2fe566d49342cbd03e49ed7db3356"
# This contract needs 60% support to pass
CURVE_ARAGON_60 = "0xbcff8b0b9419b9a88c44546519b1e909cf330399"

# Name resolution
CONTRACT_ADDR_TO_NAME = {
    OUSD: "OUSD Token",
    COMP: "COMP Token",
    VAULT: "Vault",
    MIX_ORACLE: "MixOracle",
    CHAINLINK_ORACLE: "ChainlinkOracle",
    OGN_STAKING: "OGN Staking",
    STRATCOMP1: "Compound Strategy",
    STRATCOMP2: "Compound Strategy",
    STRATAAVEDAI: "Aave Strategy",
    STRATAAVE2: "Aave Strategy",
    STRAT3POOL: "3Pool Strategy",
    COMPOUND_TIMELOCK: "Compound Timelock",
    COMPOUND_GOVERNOR_ALPHA: "Compound GovernorAlpha",
    COMPOUND_GOVERNOR_BRAVO: "Compound GovernorBravo",
    COMPOUND_COMPTROLLER: "Compound Comptroller/Unitroller",
    COMPOUND_COMPTROLLER_G7: "StdComptrollerG7",
    CDAI: "cDAI",
    CUSDT: "cUSDT",
    CUSDC: "cUSDC",
    COMPENSATION_CLAIMS: "Compensation Claims",
    CURVE_CRV_TOKEN: "CRV Token",
    CURVE_3CRV_TOKEN: "3CRV Token",
    CURVE_3POOL: "3Pool Swap Contract",
    CURVE_ARAGON_51: "Curve Aragon Voting (51%)",
    CURVE_ARAGON_60: "Curve Aragon Voting (60%)",
    GOVERNOR: "Origin Governor V1",
    GOVERNORV2: "Origin Governor V2",
    GOVERNORV3: "Origin Governor V3",
    METAMASK_SWAP_ROUTER: "Metamask Swap Router",
    FLIPPER: "OUSD Swap",
    UNISWAP_V3_ROUTER: "Uniswap V3 Router",
    OX_EXCHANGE: "0x Exchange",
    ONE_INCH_V3: "1inch V3",
    SUSHISWAP: "SushiSwap",
    UNISWAP_V2: "Uniswap V2 Router",
    MISTX_ROUTER: "MistX Router",
    CURVE_ANOTHER_3POOL: "Curve 3Pool 2",
    CURVE_METAPOOL: "Curve USDT/OUSD Metapool",
    CHAINLINK_KEEPER_REGISTRY: "Chainlink KeeperRegistry",
    OUSD_KEEPER: "OUSD Keeper",
    LINK: "LINK",
}
