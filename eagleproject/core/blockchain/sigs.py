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

# ERC20
SIG_FUNC_TOTAL_SUPPLY = encode_hex(keccak(b"totalSupply()"))
SIG_FUNC_APPROVE_AND_CALL_SENDER = encode_hex(
    keccak(b"approveAndCallWithSender(address,uint256,bytes4,bytes)")
)

# Compound
SIG_FUNC_TOTAL_BORROWS = encode_hex(keccak(b"totalBorrows()"))
SIG_FUNC_TOTAL_RESERVES = encode_hex(keccak(b"totalReserves()"))
SIG_FUNC_EXCHANGE_RATE_STORED = encode_hex(keccak(b"exchangeRateStored()"))
SIG_FUNC_BORROW_RATE = encode_hex(keccak(b"borrowRatePerBlock()"))
SIG_FUNC_SUPPLY_RATE = encode_hex(keccak(b"supplyRatePerBlock()"))
SIG_FUNC_GET_CASH = encode_hex(keccak(b"getCash()"))

# SingleAssetStaking
SIG_FUNC_DURATION_REWARD_RATE = encode_hex(
    keccak(b"durationRewardRate(uint256)")
)
SIG_FUNC_STAKE = encode_hex(keccak(b"stake(uint256,uint256)"))
SIG_FUNC_STAKE_WITH_SENDER = encode_hex(
    keccak(b"stakeWithSender(address,uint256,uint256)")
)
SIG_FUNC_AIR_DROPPED_STAKE = encode_hex(
    keccak(b"airDroppedStake(uint256,uint8,uint256,uint256,uint256,bytes32[])")
)

########
# Events
########
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"

# OGN Staking
SIG_EVENT_STAKED = encode_hex(
    keccak(b"Staked(address,uint256,uint256,uint256)")
)
SIG_EVENT_WITHDRAWN = encode_hex(keccak(b"Withdrawn(address,uint256,uint256)"))
DEPRECATED_SIG_EVENT_STAKED = encode_hex(keccak(b"Staked(address,uint256)"))
DEPRECATED_SIG_EVENT_WITHDRAWN = encode_hex(
    keccak(b"Withdrawn(address,uint256)")
)
SIG_EVENT_STAKING_PAUSED = encode_hex(keccak(b"Paused(address,bool)"))

# OUSD
SIG_EVENT_TOTAL_SUPPLY_UPDATED = encode_hex(
    keccak(b"TotalSupplyUpdated(uint256,uint256,uint256)")
)

# Vault
SIG_EVENT_MINT = encode_hex(keccak(b"Mint(address,uint256)"))
SIG_EVENT_REDEEM = encode_hex(keccak(b"Redeem(address,uint256)"))
SIG_EVENT_CAPITAL_PAUSED = encode_hex(keccak(b"CapitalPaused()"))
SIG_EVENT_CAPITAL_UNPAUSED = encode_hex(keccak(b"CapitalUnpaused()"))
SIG_EVENT_REBASE_PAUSED = encode_hex(keccak(b"RebasePaused()"))
SIG_EVENT_REBASE_UNPAUSED = encode_hex(keccak(b"RebaseUnpaused()"))
SIG_EVENT_STRATEGY_ADDED = encode_hex(keccak(b"StrategyAdded(address)"))
SIG_EVENT_STRATEGY_REMOVED = encode_hex(keccak(b"StrategyRemoved(address)"))
SIG_EVENT_WEIGHTS_UPDATED = encode_hex(
    keccak(b"StrategyWeightsUpdated(address[],uint256[])")
)
SIG_EVENT_ASSET_SUPPORTED = encode_hex(keccak(b"AssetSupported(address)"))
SIG_EVENT_BUFFER_UPDATE = encode_hex(keccak(b"VaultBufferUpdated(uint256)"))
SIG_EVENT_REDEEM_FEE = encode_hex(keccak(b"RedeemFeeUpdated(uint256)"))
SIG_EVENT_PRICE_PROVIDER = encode_hex(keccak(b"PriceProviderUpdated(address)"))
SIG_EVENT_ALLOCATE_THRESHOLD = encode_hex(keccak(b"AllocateThresholdUpdated(uint256)"))
SIG_EVENT_REBASE_THRESHOLD = encode_hex(keccak(b"RebaseThresholdUpdated(uint256)"))
SIG_EVENT_UNISWAP = encode_hex(keccak(b"UniswapUpdated(address)"))
SIG_EVENT_STRATEGIST = encode_hex(keccak(b"StrategistUpdated(address)"))
SIG_EVENT_MAX_SUPPLY_DIFF = encode_hex(keccak(b"MaxSupplyDiffChanged(uint256)"))
SIG_EVENT_DEFAULT_STRATEGY = encode_hex(keccak(b"AssetDefaultStrategyUpdated(address,address)"))
SIG_EVENT_STRATEGY_APPROVED = encode_hex(keccak(b"StrategyApproved(address)"))

# Governable
SIG_EVENT_PENDING_TRANSFER = encode_hex(keccak(b"PendingGovernorshipTransfer(address,address)"))
SIG_EVENT_TRANSFER = encode_hex(keccak(b"GovernorshipTransferred(address,address)"))

# Proxy
SIG_EVENT_UPGRADED = encode_hex(keccak(b"Upgraded(address)"))

# Timelock
SIG_EVENT_NEW_ADMIN = encode_hex(keccak(b"NewAdmin(address)"))
SIG_EVENT_NEW_PENDING_ADMIN = encode_hex(keccak(b"NewPendingAdmin(address)"))
SIG_EVENT_DELAY = encode_hex(keccak(b"NewDelay(uint256)"))

# Strategy
SIG_EVENT_DEPOSIT = encode_hex(keccak(b"Deposit(address,address,uint256)"))
SIG_EVENT_WITHDRAWAL = encode_hex(
    keccak(b"Withdrawal(address,address,uint256)")
)
SIG_EVENT_PTOKEN_ADDED = encode_hex(keccak(b"PTokenAdded(address,address)"))
SIG_EVENT_PTOKEN_REMOVED = encode_hex(
    keccak(b"PTokenRemoved(address,address)")
)
SIG_EVENT_REWARDS_COLLECTED = encode_hex(
    keccak(b"RewardTokenCollected(address,uint256)")
)

# Compound Timelock
# The following are already defined in our Timelock
# SIG_EVENT_NEW_ADMIN = encode_hex(keccak(b"NewAdmin(address)"))
# SIG_EVENT_NEW_PENDING_ADMIN = encode_hex(keccak(b"NewPendingAdmin(address)"))
# SIG_EVENT_DELAY = encode_hex(keccak(b"NewDelay(uint256)"))
SIG_EVENT_CANCEL_TRANSACTION = encode_hex(
    keccak(b"CancelTransaction(bytes32,address,uint256,string,bytes,uint256)")
)
SIG_EVENT_EXECUTE_TRANSACTION = encode_hex(
    keccak(b"ExecuteTransaction(bytes32,address,uint256,string,bytes,uint256)")
)
SIG_EVENT_QUEUE_TRANSACTION = encode_hex(
    keccak(b"QueueTransaction(bytes32,address,uint256,string,bytes,uint256)")
)

# Compound GovernorAlpha
SIG_EVENT_PROPOSAL_CREATED = encode_hex(
    keccak(b"ProposalCreated(uint256,address,address[],uint256[],string[],bytes[],uint256,uint256,string)")
)
SIG_EVENT_VOTE_CAST = encode_hex(keccak(b"VoteCast(address,uint256,bool,uint256)"))
SIG_EVENT_PROPOSAL_CANCELED = encode_hex(keccak(b"ProposalCanceled(uint256)"))
SIG_EVENT_PROPOSAL_QUEUED = encode_hex(keccak(b"ProposalQueued(uint256,uint256)"))
SIG_EVENT_PROPOSAL_EXECUTED = encode_hex(keccak(b"ProposalExecuted(uint256)"))

# Aave LendingPool
SIG_EVENT_PAUSED = encode_hex(keccak(b"Paused()"))
SIG_EVENT_UNPAUSED = encode_hex(keccak(b"Unpaused()"))

# Aave AaveProtoGovernance
SIG_EVENT_AAVE_PROPOSAL_CREATED = encode_hex(keccak(
    b"ProposalCreated(uint256,bytes32,bytes32,uint256,uint256,uint256,uint256,uint256,address)"
))
SIG_EVENT_STATUS_CHANGE_TO_VOTING = encode_hex(
    keccak(b"StatusChangeToVoting(uint256,uint256)")
)
SIG_EVENT_STATUS_CHANGE_TO_VALIDATING = encode_hex(
    keccak(b"StatusChangeToValidating(uint256)")
)
SIG_EVENT_STATUS_CHANGE_TO_EXECUTED = encode_hex(
    keccak(b"StatusChangeToExecuted(uint256)")
)
SIG_EVENT_WINS_YES = encode_hex(
    keccak(b"YesWins(uint256,uint256,uint256,uint256)")
)
SIG_EVENT_WINS_NO = encode_hex(
    keccak(b"NoWins(uint256,uint256,uint256,uint256)")
)
SIG_EVENT_WINS_ABSTAIN = encode_hex(
    keccak(b"AbstainWins(uint256,uint256,uint256,uint256)")
)

# Curve Aragon Voting fork (governance)
SIG_EVENT_START_VOTE = encode_hex(keccak(
    b"StartVote(uint256,address,string,uint256,uint256,uint256,uint256)"
))
SIG_EVENT_EXECUTE_VOTE = encode_hex(keccak(b"ExecuteVote(uint256)"))
SIG_EVENT_CHANGE_SUPPORT_REQUIRED = encode_hex(
    keccak(b"ChangeSupportRequired(uint64)")
)
SIG_EVENT_CHANGE_MIN_QUORUM = encode_hex(keccak(b"ChangeMinQuorum(uint64)"))
SIG_EVENT_MIN_BALANCE_SET = encode_hex(keccak(b"MinimumBalanceSet(uint256)"))
SIG_EVENT_MIN_TIME_SET = encode_hex(keccak(b"MinimumTimeSet(uint256)"))
SIG_EVENT_SCRIPT_RESULT = encode_hex(
    keccak(b"ScriptResult(address,bytes,bytes,bytes)")
)
SIG_EVENT_RECOVER_TO_VAULT = encode_hex(
    keccak(b"RecoverToVault(address,address,uint256)")
)
SIG_EVENT_SET_APP = encode_hex(keccak(b"SetApp(bytes32,bytes32,address)"))
SIG_EVENT_CLAIMED_TOKENS = encode_hex(
    keccak(b"ClaimedTokens(address,address,uint)")
)
SIG_EVENT_NEW_CLONE_TOKEN = encode_hex(keccak(b"NewCloneToken(address,uint)"))
