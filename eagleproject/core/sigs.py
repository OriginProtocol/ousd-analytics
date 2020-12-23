from eth_hash.auto import keccak
from eth_utils import encode_hex

# getPrice(address source, string calldata key)
OPEN_ORACLE_GET_PRICE = encode_hex(keccak(b"getPrice(address,string)"))
# ethUsdPrice() - uint256 (6-decimal USD)
CHAINLINK_ETH_USD_PRICE = encode_hex(keccak(b"ethUsdPrice()"))
# tokEthPrice(string calldata symbol)
CHAINLINK_TOK_ETH_PRICE = encode_hex(keccak(b"tokEthPrice(string)"))
# tokUsdPrice(string calldata symbol)
CHAINLINK_TOK_USD_PRICE = encode_hex(keccak(b"tokUsdPrice(string)"))

# Events
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
SIG_EVENT_STAKED = encode_hex(keccak(b"Staked(address,uint256)"))
SIG_EVENT_WITHDRAWN = encode_hex(keccak(b"Withdrawn(address,uint256)"))
