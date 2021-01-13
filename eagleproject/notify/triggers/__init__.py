""" Every file in this dir (that doesn't start with __) is an individual trigger
that when run, processes the analytics data of its choosing looking to meet
specific conditions.  If a condition is met, it will return the events it
thinks are relevant.

Every trigger should implement:
 - run_trigger() -> List[Event]

 Every run_trigger() implementation can accept any of these kwargs:

 - latest_block - The latest known block number according to the RPC source
 - transfer_cursor - A NotifyCursor model for transfers
 - transaction_cursor - A NotifyCursor model for transactions
 - transfers - All transfers
 - new_transfers - All new transfers since the last update
 - transactions - All transactions
 - new_transactions - All new transactions since the last run
 - logs - All logs
 - new_logs - All new logs since the last run
 - ogn_staking_snapshot - Latest OGN staking snapshot
 - oracle_snapshots - Oracle snapshot for a specific block
 - ctoken_snapshots - Retreives the cToken snapshots for a specific block
 - recent_ctoken_snapshots - Retrieves the cToken snapshots for the last N
    snapshots
"""
import inspect
import logging
from pathlib import Path
from datetime import datetime
from importlib import import_module
from django.db.models import Max, Subquery

from core.models import (
    CTokenSnapshot,
    Block,
    Log,
    OgnStakingSnapshot,
    OracleSnapshot,
    OusdTransfer,
    SupplySnapshot,
    Transaction,
)
from notify.models import CursorId, NotifyCursor

ME = Path(__file__).resolve()
THIS_DIR = ME.parent
SKIP_TRIGGERS = ['noop']
log = logging.getLogger('notify.triggers')


def strip_ext(fname):
    """ Strip an extension from a filename """
    if '.' not in fname:
        return fname
    return '.'.join(fname.split('.')[:-1])


def load_triggers():
    """ Loads all trigger modules in this dir """
    files = [
        x
        for x in THIS_DIR.iterdir()
        if (
            x.is_file()
            and x.name.endswith('.py')
            and not x.name.startswith('__')
        )
    ]

    return [
        import_module('notify.triggers.{}'.format(strip_ext(mod.name)))
        for mod in files
        if strip_ext(mod.name) not in SKIP_TRIGGERS
    ]


def transfers(block_number):
    """ Get all transfers since given block """
    return OusdTransfer.objects.filter(tx_hash__block_number__gt=block_number)


def transactions(block_number):
    """ Get all transactions since given block """
    return Transaction.objects.filter(block_number__gt=block_number)


def logs(block_number):
    """ Get all event logs since given block """
    return Log.objects.filter(block_number__gt=block_number)


def latest_ogn_staking_snap():
    try:
        return OgnStakingSnapshot.objects.all().order_by('-block_number')[0]
    except Exception as e:
        print('e:', e)
        return None


def oracles_snaps(block_number):
    return OracleSnapshot.objects.filter(block_number=block_number)


def ctoken_snapshots(block_number):
    return CTokenSnapshot.objects.filter(block_number=block_number)


def recent_ctoken_snapshots(snap_count=5):
    """ Get the latest N snapshots for all cTokens """
    return CTokenSnapshot.objects.annotate(
        block_number__in=Subquery(
            CTokenSnapshot.objects.order_by(
                '-block_number'
            ).values('block_number')[:snap_count]
        )
    ).order_by('-block_number', 'address')


def run_all_triggers():
    """ Run all triggers """
    events = []
    mods = load_triggers()

    # Source from the DB to prevent a race with data collection
    max_block = Block.objects.all().aggregate(Max("block_number"))
    max_snapshot_block = SupplySnapshot.objects.all().aggregate(
        Max("block_number")
    )
    block_number = 0
    snapshot_block_number = 0

    if max_block:
        block_number = max_block.get("block_number__max", 0)
    if max_snapshot_block:
        snapshot_block_number = max_snapshot_block.get("block_number__max", 0)

    transfer_cursor, _ = NotifyCursor.objects.get_or_create(
        cursor_id=CursorId.TRANSFERS,
        defaults={
            "block_number": block_number,
            "last_update": datetime.utcnow(),
        }
    )

    transaction_cursor, _ = NotifyCursor.objects.get_or_create(
        cursor_id=CursorId.TRANSACTIONS,
        defaults={
            "block_number": block_number,
            "last_update": datetime.utcnow(),
        }
    )

    snapshot_cursor, _ = NotifyCursor.objects.get_or_create(
        cursor_id=CursorId.SNAPSHOT,
        defaults={
            "block_number": snapshot_block_number,
            "last_update": datetime.utcnow(),
        }
    )

    availible_kwargs_valgen = {
        "latest_block": lambda: block_number,
        "latest_snapshot_block": lambda: snapshot_block_number,
        "snapshot_cursor": lambda: snapshot_cursor,
        "transfer_cursor": lambda: transfer_cursor,
        "transaction_cursor": lambda: transaction_cursor,
        "transactions": lambda: transactions(transaction_cursor.block_number),
        "new_transactions": lambda: transactions(
            transaction_cursor.block_number
        ),
        "transfers": lambda: transfers(0),
        "new_transfers": lambda: transfers(transfer_cursor.block_number),
        "logs": lambda: logs(0),
        "new_logs": lambda: logs(transaction_cursor.block_number),
        "ogn_staking_snapshot": latest_ogn_staking_snap,
        "oracle_snapshots": lambda: oracles_snaps(snapshot_block_number),
        "ctoken_snapshots": lambda: ctoken_snapshots(
            snapshot_block_number
        ),
        "recent_ctoken_snapshots": lambda: recent_ctoken_snapshots()
    }

    for mod in mods:
        # Figure out the kwargs it wants
        func_spec = inspect.getfullargspec(mod.run_trigger)

        # Give it values
        script_kwargs = {
            k: availible_kwargs_valgen[k]() for k in func_spec.args
        }

        try:
            # Execute and save actions for return
            events.extend(mod.run_trigger(**script_kwargs))
        except Exception:
            log.exception("Exception occurred running trigger")

    if transfer_cursor.block_number != block_number:
        transfer_cursor.block_number = block_number
        transfer_cursor.last_update = datetime.utcnow()
        transfer_cursor.save()

    if transaction_cursor.block_number != block_number:
        transaction_cursor.block_number = block_number
        transaction_cursor.last_update = datetime.utcnow()
        transaction_cursor.save()

    if snapshot_cursor.block_number != snapshot_block_number:
        snapshot_cursor.block_number = snapshot_block_number
        snapshot_cursor.last_update = datetime.utcnow()
        snapshot_cursor.save()

    return events
