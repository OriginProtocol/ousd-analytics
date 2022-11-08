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

# Chainlink KeeperRegistry
EVENT_KEEPER_UPKEEP_PERFORMED = encode_hex(
    keccak(b"UpkeepPerformed(uint256,bool,address,uint96,bytes)")
)
EVENT_KEEPER_UPKEEP_CANCELLED = encode_hex(
    keccak(b"UpkeepCanceled(uint256,uint64)")
)
EVENT_KEEPER_FUNDS_ADDED = encode_hex(
    keccak(b"FundsAdded(uint256,address,uint96)")
)
EVENT_KEEPER_FUNDS_WITHDRAWN = encode_hex(
    keccak(b"FundsWithdrawn(uint256,uint256,address)")
)

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

# DRIPPER
SIG_DRIPPER_AVAILABLE_FUNDS = encode_hex(keccak(b"availableFunds()"))
SIG_DRIPPER_CONFIG = encode_hex(keccak(b"drip()"))

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

# Story Staking
SIG_FUNC_CURRENT_CLAIMING_INDEX = encode_hex(keccak(b"currentClaimingIndex()"))
SIG_FUNC_CURRENT_STAKING_INDEX = encode_hex(keccak(b"currentStakingIndex()"))
# NewSeason(uint256 indexed number, address indexed season)
SIG_EVENT_NEW_SEASON = encode_hex(keccak(b"NewSeason(uint256,address)"))
# SeasonStart(uint256 indexed number, address indexed season)
SIG_EVENT_SEASON_START = encode_hex(keccak(b"SeasonStart(uint256,address)"))
# SeasonCancelled(address indexed season)
SIG_EVENT_SEASON_CANCELLED = encode_hex(keccak(b"SeasonCancelled(address)"))
# Stake(address indexed userAddress, uint256 indexed amount, uint256 points)
SIG_EVENT_STAKE = encode_hex(keccak(b"Stake(address,uint256,uint256)"))
# Unstake(address indexed userAddress)
SIG_EVENT_UNSTAKE = encode_hex(keccak(b"Unstake(address)"))
# Finale(uint256 totalRewardETH, uint256 totalRewardOGN)
SIG_EVENT_FINALE = encode_hex(keccak(b"Finale(uint256,uint256)"))
# RewardsSent(address indexed asset, address indexed toAddress, uint256 amount)
SIG_EVENT_REWARDS_SENT = encode_hex(
    keccak(b"RewardsSent(address,address,uint256)")
)
# NewController(address controllerAddress)
SIG_EVENT_NEW_CONTROLLER = encode_hex(keccak(b"NewController(address)"))

# OpenZeppelin Pausable
# Paused(address account)
SIG_EVENT_OZ_PAUSED = encode_hex(keccak(b"Paused(address)"))
# Unpaused(address account)
SIG_EVENT_OZ_UNPAUSED = encode_hex(keccak(b"Unpaused(address)"))

# OUSD
SIG_EVENT_TOTAL_SUPPLY_UPDATED = encode_hex(
    keccak(b"TotalSupplyUpdated(uint256,uint256,uint256)")
)
SIG_EVENT_TOTAL_SUPPLY_UPDATED_HIRES = encode_hex(
    keccak(b"TotalSupplyUpdatedHighres(uint256,uint256,uint256)")
)

# Vault
SIG_FUNC_PRICE_USD_MINT = encode_hex(keccak(b"priceUSDMint(address)"))
SIG_FUNC_PRICE_USD_REDEEM = encode_hex(keccak(b"priceUSDRedeem(address)"))
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
SIG_EVENT_ALLOCATE_THRESHOLD = encode_hex(
    keccak(b"AllocateThresholdUpdated(uint256)")
)
SIG_EVENT_REBASE_THRESHOLD = encode_hex(
    keccak(b"RebaseThresholdUpdated(uint256)")
)
SIG_EVENT_UNISWAP = encode_hex(keccak(b"UniswapUpdated(address)"))
SIG_EVENT_STRATEGIST = encode_hex(keccak(b"StrategistUpdated(address)"))
SIG_EVENT_MAX_SUPPLY_DIFF = encode_hex(keccak(b"MaxSupplyDiffChanged(uint256)"))
SIG_EVENT_DEFAULT_STRATEGY = encode_hex(
    keccak(b"AssetDefaultStrategyUpdated(address,address)")
)
SIG_EVENT_STRATEGY_APPROVED = encode_hex(keccak(b"StrategyApproved(address)"))
SIG_EVENT_YIELD_DISTRIBUTION = encode_hex(
    keccak(b"YieldDistribution(address,uint256,uint256)")
)
SIG_EVENT_TRUSTEE_FEE_CHANGED = encode_hex(
    keccak(b"TrusteeFeeBpsChanged(uint256)")
)
SIG_EVENT_TRUSTEE_ADDRESS_CHANGED = encode_hex(
    keccak(b"TrusteeAddressChanged(address)")
)

# Governable
SIG_EVENT_PENDING_TRANSFER = encode_hex(
    keccak(b"PendingGovernorshipTransfer(address,address)")
)
SIG_EVENT_TRANSFER = encode_hex(
    keccak(b"GovernorshipTransferred(address,address)")
)

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
SIG_EVENT_PTOKEN_REMOVED = encode_hex(keccak(b"PTokenRemoved(address,address)"))
SIG_EVENT_REWARDS_COLLECTED = encode_hex(
    keccak(b"RewardTokenCollected(address,uint256)")
)
SIG_EVENT_MAX_SLIPPAGE_UPDATED = encode_hex(
    keccak(b"MaxWithdrawalSlippageUpdated(uint256,uint256)")
)
SIG_EVENT_REWARD_TOKENS_UPDATED = encode_hex(
    keccak(b"RewardTokenAddressesUpdated(address[],address[])")
)
SIG_EVENT_HARVESTER_UPDATED = encode_hex(
    keccak(b"HarvesterAddressesUpdated(address,address)")
)

# OUSD Timelock
SIG_EVENT_CALL_SCHEDULED = encode_hex(
    keccak(b"CallScheduled(bytes32,uint256,address,uint256,bytes,bytes32,uint256)")
)
SIG_EVENT_CALL_EXECUTED = encode_hex(
    keccak(b"CallExecuted(bytes32,uint256,address,uint256,bytes)")
)
SIG_EVENT_CALL_CANCELLED = encode_hex(
    keccak(b"Cancelled(bytes32)")
)
SIG_EVENT_MIN_DELAY_CHANGED = encode_hex(
    keccak(b"MinDelayChange(uint256,uint256)")
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

SIG_EVENT_ROLE_ADMIN_CHANGED = encode_hex(
    keccak(b"RoleAdminChanged(bytes32,bytes32,bytes32")
)
SIG_EVENT_ROLE_GRANTED = encode_hex(
    keccak(b"RoleGranted(bytes32,address,address")
)
SIG_EVENT_ROLE_REVOKED = encode_hex(
    keccak(b"RoleRevoked(bytes32,address,address")
)

# Compound GovernorAlpha, GovernorBravo
# OUSD Governance
SIG_EVENT_PROPOSAL_CREATED = encode_hex(
    keccak(
        b"ProposalCreated(uint256,address,address[],uint256[],string[],bytes[],uint256,uint256,string)"
    )
)
# VoteCast(address voter, uint proposalId, bool support, uint votes);
SIG_EVENT_VOTE_CAST = encode_hex(
    keccak(b"VoteCast(address,uint256,bool,uint256)")
)
SIG_EVENT_VOTE_CAST_OUSD = encode_hex(
    keccak(b"VoteCast(address,uint256,uint8,uint256,string)")
)
SIG_EVENT_PROPOSAL_CANCELED = encode_hex(keccak(b"ProposalCanceled(uint256)"))
SIG_EVENT_PROPOSAL_QUEUED = encode_hex(
    keccak(b"ProposalQueued(uint256,uint256)")
)
SIG_EVENT_PROPOSAL_EXECUTED = encode_hex(keccak(b"ProposalExecuted(uint256)"))

# Compound GovernorBravo specific
# VoteCast(address indexed voter, uint proposalId, uint8 support, uint votes, string reason);
SIG_EVENT_VOTE_CAST_BRAVO = encode_hex(
    keccak(b"VoteCast(address,uint,uint8,uint256,string)")
)
# NewImplementation(address oldImplementation, address newImplementation);
SIG_EVENT_NEW_IMPLEMENTATION_BRAVO = encode_hex(
    keccak(b"NewImplementation(address,address)")
)
# VotingDelaySet(uint oldVotingDelay, uint newVotingDelay)
SIG_EVENT_VOTING_DELAY_SET = encode_hex(keccak(b"VotingDelaySet(uint,uint)"))
# VotingPeriodSet(uint oldVotingPeriod, uint newVotingPeriod)
SIG_EVENT_VOTING_PERIOD_SET = encode_hex(keccak(b"VotingPeriodSet(uint,uint)"))
# ProposalThresholdSet(uint oldProposalThreshold, uint newProposalThreshold)
SIG_EVENT_PROPOSAL_THRESHOLD_SET = encode_hex(
    keccak(b"ProposalThresholdSet(uint,uint)")
)
# NewPendingAdmin(address oldPendingAdmin, address newPendingAdmin)
SIG_EVENT_NEW_PENDING_ADMIN_BRAVO = encode_hex(
    keccak(b"NewPendingAdmin(address,address)")
)
# NewAdmin(address oldAdmin, address newAdmin)
SIG_EVENT_NEW_ADMIN_BRAVO = encode_hex(keccak(b"NewAdmin(address,address)"))

# OUSD Governance
SIG_EVENT_QUORUM_NUMERATOR_UPDATED = encode_hex(keccak(b"QuorumNumeratorUpdated(uint256,uint256"))
SIG_EVENT_TIMELOCK_CHANGE = encode_hex(keccak(b"TimelockChange(address,address"))
SIG_EVENT_LATE_QUORUM_VOTE_EXTENSION_SET = encode_hex(keccak(b"LateQuorumVoteExtensionSet(uint64,uint64"))
SIG_EVENT_PROPOSAL_EXTENDED = encode_hex(keccak(b"ProposalExtended(uint256,uint64"))

# Aave LendingPool
SIG_EVENT_PAUSED = encode_hex(keccak(b"Paused()"))
SIG_EVENT_UNPAUSED = encode_hex(keccak(b"Unpaused()"))

# Aave AaveProtoGovernance
SIG_EVENT_AAVE_PROPOSAL_CREATED = encode_hex(
    keccak(
        b"ProposalCreated(uint256,bytes32,bytes32,uint256,uint256,uint256,uint256,uint256,address)"
    )
)
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
SIG_EVENT_START_VOTE = encode_hex(
    keccak(b"StartVote(uint256,address,string,uint256,uint256,uint256,uint256)")
)
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
