from eth_hash.auto import keccak
from eth_utils import encode_hex

# getPrice(address source, string calldata key)
OPEN_ORACLE_GET_PRICE = encode_hex(keccak(b"getPrice(address,string)"))
# price(string calldata symbol)
OPEN_ORACLE_PRICE = encode_hex(keccak(b"price(string)"))
# ethUsdPrice() - uint256 (6-decimal USD)
CHAINLINK_ETH_USD_PRICE = encode_hex(keccak(b"ethUsdPrice()"))
# tokEthPrice(string calldata symbol)
CHAINLINK_TOK_ETH_PRICE = encode_hex(keccak(b"tokEthPrice(string)"))
# tokUsdPrice(string calldata symbol)
CHAINLINK_TOK_USD_PRICE = encode_hex(keccak(b"tokUsdPrice(string)"))

########
# Events
########
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"

# OGN Staking
SIG_EVENT_STAKED = encode_hex(keccak(b"Staked(address,uint256)"))
SIG_EVENT_WITHDRAWN = encode_hex(keccak(b"Withdrawn(address,uint256)"))

# OUSD
SIG_EVENT_TOTAL_SUPPLY_UPDATED = encode_hex(
    keccak(b"TotalSupplyUpdated(uint256,uint256,uint256)")
)

# Vault
SIG_EVENT_MINT = encode_hex(keccak(b"Mint(address,uint256)"))
SIG_EVENT_REDEEM = encode_hex(keccak(b"Redeem(address,uint256)"))

# Strategy
SIG_EVENT_DEPOSIT = encode_hex(keccak(b"Deposit(address,address,uint256)"))
SIG_EVENT_WITHDRAWAL = encode_hex(keccak(b"Withdrawal(address,address,uint256)"))
SIG_EVENT_PTOKEN_ADDED = encode_hex(keccak(b"Deposit(address,address,uint256)"))
SIG_EVENT_PTOKEN_REMOVED = encode_hex(keccak(b"Deposit(address,address,uint256)"))
SIG_EVENT_REWARDS_COLLECTED = encode_hex(
    keccak(b"RewardTokenCollected(address,uint256)")
)
