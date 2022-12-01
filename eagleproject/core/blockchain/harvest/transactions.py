from datetime import datetime, timedelta
from django import db
from multiprocessing import Process
from django.conf import settings
from eth_abi import decode_single
from eth_utils import (
    decode_hex,
    encode_hex,
    add_0x_prefix,
    remove_0x_prefix,
)

from core.etherscan import get_contract_transactions, get_internal_txs_bt_txhash
from core.blockchain.addresses import (
    OGN,
    OGN_STAKING,
    STORY_STAKING_SERIES,
    STORY_STAKING_SEASONS,
)
from core.blockchain.const import (
    E_18,
    ETHERSCAN_CONTRACTS,
    LOG_CONTRACTS,
    START_OF_EVERYTHING,
    START_OF_OUSD_TOTAL_SUPPLY_UPDATED_HIGHRES,
)
from core.blockchain.conversion import human_duration_yield
from core.blockchain.decode import decode_args, slot
from core.blockchain.harvest.blocks import ensure_block
from core.blockchain.rpc import (
    debug_trace_transaction,
    get_transaction,
    get_transaction_receipt,
    request,
    staking_durationRewardRate,
)

from core.blockchain.utils import (
    chunks,
)

from core.blockchain.sigs import (
    DEPRECATED_SIG_EVENT_WITHDRAWN,
    DEPRECATED_SIG_EVENT_STAKED,
    SIG_EVENT_ERC20_TRANSFER,
    SIG_EVENT_STAKE,
    SIG_EVENT_STAKED,
    SIG_EVENT_UNSTAKE,
    SIG_EVENT_WITHDRAWN,
    SIG_FUNC_APPROVE_AND_CALL_SENDER,
    SIG_FUNC_AIR_DROPPED_STAKE,
    SIG_FUNC_STAKE,
    SIG_FUNC_STAKE_WITH_SENDER,
    TRANSFER,
)
from core.logging import get_logger
from core.models import (
    DebugTx,
    EtherscanPointer,
    Log,
    LogPointer,
    OgnStaked,
    OusdTransfer,
    StoryStake,
    Transaction,
)

logger = get_logger(__name__)


def build_debug_tx(tx_hash):
    data = debug_trace_transaction(tx_hash)
    return DebugTx(tx_hash=tx_hash, block_number=0, data=data["result"])


def ensure_all_transactions(block_number):
    """Verify we have all transactions using Etherscan as a secondary source of
    transaction data.  This has the benefit of including failed transactions
    and transactions that do not generate logs.
    """
    pointers = {x.contract: x for x in EtherscanPointer.objects.all()}
    if settings.ETHERSCAN_API_KEY:
        for address in ETHERSCAN_CONTRACTS:
            if address not in pointers:
                pointers[address] = EtherscanPointer.objects.create(
                    contract=address,
                    last_block=0,
                )

            tx_hashes = []
            for tx in get_contract_transactions(
                address, pointers[address].last_block, block_number
            ):
                if tx.get("hash") is None:
                    logger.error("No transaction hash found from Etherscan")
                    continue
                tx_hashes.append(tx["hash"])

            ensure_transaction_and_downsteam_hashes(tx_hashes)

            pointers[address].last_block = block_number
            pointers[address].save()


def maybe_store_transfer_record(log, block):
    # Must be a transfer event
    if log["topics"][0] != TRANSFER:
        return None

    # Must be on OUSD
    if log["address"] != "0x2a8e1e676ec238d8a992307b495b45b3feaa5e86":
        return None

    tx_hash = log["transactionHash"]
    log_index = int(log["logIndex"], 16)

    params = {
        "block_time": block.block_time,
        "from_address": "0x" + log["topics"][1][-40:],
        "to_address": "0x" + log["topics"][2][-40:],
        "amount": int(slot(log["data"], 0), 16) / E_18,
    }

    transfer, created = OusdTransfer.objects.get_or_create(
        tx_hash_id=tx_hash, log_index=log_index, defaults=params
    )

    if not created:
        transfer.conditional_update(**params)

    return transfer


def explode_log_data(value):
    count = len(value) // 64
    out = []
    for i in range(0, count):
        out.append(int(value[2 + i * 64 : 2 + i * 64 + 64], 16) / 1e18)
    return out

# get rebase log at block number
def get_rebase_log(block_number):
    rebase_log = Log.objects.filter(
        topic_0='0x09516ecf4a8a86e59780a9befc6dee948bc9e60a36e3be68d31ea817ee8d2c80',
        block_number__lte=block_number
    ).order_by('-block_number')[:1].get()

    return rebase_log

# get rebasing credits per token log at block number
def get_rebasing_credits_per_token(block_number):
    print("block_number", block_number)
    rebase_log = get_rebase_log(block_number)
    explode_log_data(rebase_log.data)

    credits_per_token = explode_log_data(rebase_log.data)[2]
    # we have increased the accuracy from 1e18 to 1e27 for rebasing credits per token
    # at that block number
    if (block_number >= START_OF_OUSD_TOTAL_SUPPLY_UPDATED_HIGHRES):
        return credits_per_token / 1e9

    return credits_per_token

def get_internal_transactions(tx_hash):
    data = get_internal_txs_bt_txhash(tx_hash)
    return data


def ensure_transaction_and_downstream(tx_hash):
    """ Ensure that there's a transaction record """
    db_tx = None
    block = None
    receipt = None

    raw_transaction = get_transaction(tx_hash)
    receipt = get_transaction_receipt(tx_hash)
    debug = debug_trace_transaction(tx_hash)
    internal_transactions = get_internal_transactions(tx_hash)

    block_number = int(raw_transaction["blockNumber"], 16)
    block = ensure_block(block_number)

    params = {
        "block_number": block_number,
        "block_time": block.block_time,
        "data": raw_transaction,
        "receipt_data": receipt,
        "debug_data": debug,
        "internal_transactions": internal_transactions,
        "from_address": receipt["from"],
        "to_address": receipt.get("to"),
    }

    db_tx, created = Transaction.objects.get_or_create(
        tx_hash=tx_hash, defaults=params
    )

    if not created:
        db_tx.conditional_update(**params)

    for log in receipt["logs"]:
        ensure_log_record(log)
        maybe_store_transfer_record(log, block)
        maybe_store_stake_withdrawn_record(log, block)
        maybe_store_stake(log, block, receipt)

    print(f"Transaction {tx_hash} ensured.")
    print(f"Block {block_number} ensured.")

    return db_tx


def ensure_log_record(raw_log):
    block_number = int(raw_log["blockNumber"], 16)
    log_index = int(raw_log["logIndex"], 16)
    transaction_index = int(raw_log["transactionIndex"], 16)

    log = None
    topic_0 = ""
    topic_1 = ""
    topic_2 = ""
    topic_3 = ""

    if len(raw_log["topics"]) >= 1:
        topic_0 = raw_log["topics"][0]
    if len(raw_log["topics"]) >= 2:
        topic_1 = raw_log["topics"][1]
    if len(raw_log["topics"]) >= 3:
        topic_2 = raw_log["topics"][2]
    if len(raw_log["topics"]) == 4:
        topic_3 = raw_log["topics"][3]

    params = {
        "address": raw_log["address"],
        "transaction_hash": raw_log["transactionHash"],
        "transaction_index": transaction_index,
        "data": raw_log["data"],
        "event_name": "",
        "topic_0": topic_0,
        "topic_1": topic_1,
        "topic_2": topic_2,
        "topic_3": topic_3,
    }

    log, created = Log.objects.get_or_create(
        block_number=block_number,
        transaction_index=transaction_index,
        log_index=log_index,
        defaults=params,
    )

    if not created:
        log.conditional_update(**params)

    return log


def ensure_transaction_and_downsteam_hashes(tx_hashes):
    for tx_hash in tx_hashes:
        ensure_transaction_and_downstream(tx_hash)


def ensure_transaction_and_downsteam_in_paralel(tx_hashes, totalProcessed):
    print(
        "Processing {} transactions of total processed {}".format(
            len(tx_hashes), totalProcessed
        )
    )
    processes = []

    # Multiprocessing copies connection objects between processes because it forks processes
    # and therefore copies all the file descriptors of the parent process. That being said,
    # a connection to the SQL server is just a file, you can see it in linux under /proc//fd/....
    # any open file will be shared between forked processes.
    # closing all connections just forces the processes to open new connections within the new
    # process.
    # Not doing this causes PSQL connection errors because multiple processes are using a single connection in
    # a non locking manner.
    db.connections.close_all()
    for tx_hash in tx_hashes:
        p = Process(target=ensure_transaction_and_downstream, args=(tx_hash,))
        p.start()
        processes.append(p)
    for p in processes:
        p.join()


def download_logs_from_contract(contract, start_block, end_block):
    print(
        f"download_logs_from_contract({contract}, {start_block}, {end_block})"
    )
    logger.info("D {} {} {}".format(contract, start_block, end_block))
    data = request(
        "eth_getLogs",
        [
            {
                "fromBlock": hex(start_block),
                "toBlock": hex(end_block),
                "address": contract,
            }
        ],
    )

    tx_hashes = set([x["transactionHash"] for x in data["result"]])

    ensure_transaction_and_downsteam_hashes(list(tx_hashes))


def ensure_latest_logs(upto):
    pointers = {x.contract: x for x in LogPointer.objects.all()}
    # Keep in mind that GAE isn't best suited for parallelism. And if we were to go for it
    # we need to improve the error handling.
    for contract in LOG_CONTRACTS:
        ensure_latest_logs_for_contract(contract, pointers, upto)


def ensure_latest_logs_for_contract(contract, pointers, upto):
    pointer = None
    if contract not in pointers:
        pointer = LogPointer(contract=contract, last_block=START_OF_EVERYTHING)
        pointer.save()
    else:
        pointer = pointers[contract]
    start_block = pointer.last_block + 1
    while start_block <= upto:
        end_block = min(start_block + 1000, upto)
        download_logs_from_contract(contract, start_block, end_block)
        pointer.last_block = end_block
        pointer.save()
        start_block = pointer.last_block + 1


def maybe_store_stake_withdrawn_record(log, block):
    # Must be a Staked or Withdrawn event
    if log["address"] != OGN_STAKING or log["topics"][0] not in [
        SIG_EVENT_STAKED,
        SIG_EVENT_WITHDRAWN,
        DEPRECATED_SIG_EVENT_STAKED,
        DEPRECATED_SIG_EVENT_WITHDRAWN,
    ]:
        return None

    tx_hash = log["transactionHash"]
    log_index = int(log["logIndex"], 16)

    is_updated_staked_event = log["topics"][0] == SIG_EVENT_STAKED
    is_withdrawn_event = log["topics"][0] == SIG_EVENT_WITHDRAWN
    is_staked_event = (
        log["topics"][0] == DEPRECATED_SIG_EVENT_STAKED
        or is_updated_staked_event
    )
    staker = add_0x_prefix(log["topics"][1][-40:])

    duration = 0
    rate = 0
    stake_type = 0
    amount = 0

    tx = get_transaction(tx_hash)
    tx_input = tx.get("input")

    if tx and tx_input and len(tx_input) > 10:
        call_sig = tx_input[:10]

        # Unpack if it was called through OGN's approveAndCallWithSender...
        if call_sig == SIG_FUNC_APPROVE_AND_CALL_SENDER[:10]:
            _, _, selector, calldata = decode_args(
                "approveAndCallWithSender(address,uint256,bytes4,bytes)",
                decode_hex("0x{}".format(tx_input[10:])),
            )

            call_sig = encode_hex(selector)

            # approveAndCallWithSender always uses `msg.sender` as the first
            # arg of the subsequent function call.  For our purposes we're
            # going to assume the `Staked` event we decoded before is correct
            # and use its `user` argument.  Otherwise, we'd have to figure out
            # what sender was before in the call chain or rely on the
            # expectation that `tx.origin` is the same as `msg.sender`, which
            # is less likely to be true than the event being wrong.
            #
            # Ref: https://github.com/OriginProtocol/origin/blob/master/packages/contracts/contracts/token/OriginToken.sol#L70-L105
            packed_staker = decode_hex(remove_0x_prefix(staker).rjust(64, "0"))
            tx_input = encode_hex(selector + packed_staker + calldata)

        # stakeWithSender(address staker, uint256 amount, uint256 duration)
        if call_sig == SIG_FUNC_STAKE_WITH_SENDER[:10]:
            _staker, _amount, _duration = decode_args(
                "stakeWithSender(address,uint256,uint256)",
                decode_hex(tx_input[10:]),
            )

            if _staker != staker:
                logger.warning(
                    "Unexpected staker address {} != {}. Something is quite "
                    "wrong.".format(
                        staker,
                        _staker,
                    )
                )

            _rate = staking_durationRewardRate(
                OGN_STAKING, _duration, int(tx["blockNumber"], 16)
            )

            amount = _amount / E_18
            duration, rate = human_duration_yield(_duration, _rate)

        # stake(uint256 amount, uint256 duration)
        elif call_sig == SIG_FUNC_STAKE[:10]:
            _amount, _duration = decode_args(
                "stake(uint256,uint256)", decode_hex(tx_input[10:])
            )

            _rate = staking_durationRewardRate(
                OGN_STAKING, _duration, int(tx["blockNumber"], 16)
            )

            amount = _amount / E_18
            duration, rate = human_duration_yield(_duration, _rate)

        # airDroppedStake(uint256 index, uint8 stakeType,
        #                 uint256 duration, uint256 rate,
        #                 uint256 amount,
        #                 bytes32[] calldata merkleProof)
        elif call_sig == SIG_FUNC_AIR_DROPPED_STAKE[:10]:
            (index, stake_type, _duration, _rate, _amount, _,) = decode_args(
                "airDroppedStake(uint256,uint8,uint256,uint256,uint256,bytes32[])",
                decode_hex(tx_input[10:]),
            )

            amount = _amount / E_18
            duration, rate = human_duration_yield(_duration, _rate)

        else:
            logger.warning(
                "Do not recognize call signature: {}".format(call_sig)
            )

            """ In certain cases, we're unable to decode the function call
            because it's wrapped by something else.  For instance, a wallet
            proxy contract.  We'll try to fall back to the amount from the
            event if available
            """
            if amount < 1:
                amount = int(slot(log["data"], 0), 16) / E_18

    # Fallback to decoding from newer events if available
    if duration == 0 and is_updated_staked_event:
        _duration = slot(log["data"], 1)
        _rate = slot(log["data"], 2)
        duration, rate = human_duration_yield(_duration, _rate)

    params = {
        "block_time": block.block_time,
        "user_address": staker,
        "is_staked": is_staked_event,
        "amount": amount,
        # This is apparently withdrawn amount and the name makes no sense
        "staked_amount": int(slot(log["data"], 1), 16) / E_18
        if is_withdrawn_event
        else 0,
        "duration": duration,
        "staked_duration": timedelta(days=duration),
        "rate": rate,
        "stake_type": stake_type,
    }

    staked, created = OgnStaked.objects.get_or_create(
        tx_hash=tx_hash,
        log_index=log_index,
        defaults=params,
    )

    if not created:
        staked.conditional_update(**params)
        staked.save()

    return staked


def receipt_has_unstake_transfer(receipt):
    """ Check if the receipt has an OGN transfer from the Series contract """
    return any(
        log["address"] == OGN
        and log["topics"][0] == SIG_EVENT_ERC20_TRANSFER
        and decode_single("(address)", decode_hex(log["topics"][1]))[0]
        == STORY_STAKING_SERIES
        for log in receipt["logs"]
    )


def maybe_store_stake(log, block, receipt):
    """ Store a story stake record """

    if log["address"] not in STORY_STAKING_SEASONS:
        return None

    log_index = int(log["logIndex"], 16)

    if log["topics"][0] == SIG_EVENT_STAKE:
        params = {
            "tx_hash": log["transactionHash"],
            "user_address": add_0x_prefix(log["topics"][1][-40:]),
            "amount": int(log["topics"][2], 16),
            "points": int(slot(log["data"], 0), 16),
        }

        stake, created = StoryStake.objects.get_or_create(
            block=block,
            log_index=log_index,
            defaults=params,
        )

        if not created:
            stake.conditional_update(**params)
            stake.save()

        return stake

    elif log["topics"][0] == SIG_EVENT_UNSTAKE:
        user_address = add_0x_prefix(log["topics"][1][-40:])

        # Many Unstake events from Season contracts are claims (because it's the
        # same thing to the Season), but do not actually unstake from the
        # Series.  Check for a transfer of OGN from Series to the user to
        # detect an actual unstake.
        if receipt_has_unstake_transfer(receipt):
            # Unstakes are for the full stake amount
            StoryStake.objects.filter(
                user_address=user_address, unstake_block__isnull=True
            ).update(unstake_block=block)

    return None
