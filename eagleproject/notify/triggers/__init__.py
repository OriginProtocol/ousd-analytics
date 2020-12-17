""" Every file in this dir (that doesn't start with __) is an individual trigger
that when run, processes the analytics data of its choosing looking to meet
specific conditions.  If a condition is met, it will return the events it
thinks are relevant.

Every trigger should implement:
 - run_trigger() -> List[Event]

 Every run_trigger() implementation can accept any of these kwargs:

 - transfer_cursor - A NotifyCursor model for transfers
 - transaction_cursor - A NotifyCursor model for transactions
 - transfers - All transfers
 - new_transfers - All new transfers since the last update
 - transactions - All transactions
 - new_transactions - All new transactions since the last run
 - logs - All logs
 - new_logs - All new logs since the last run
"""
import inspect
from pathlib import Path
from datetime import datetime
from importlib import import_module

from core.blockchain import latest_block
from core.models import Log, OusdTransfer, Transaction
from notify.models import CursorId, NotifyCursor

ME = Path(__file__).resolve()
THIS_DIR = ME.parent
SKIP_TRIGGERS = ['noop']


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
        if x.is_file() and not x.name.startswith('__')
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


def run_all_triggers():
    """ Run all triggers """
    events = []
    mods = load_triggers()

    block_number = latest_block()

    transfer_cursor, _ = NotifyCursor.objects.get_or_create(
        cursor_id=CursorId.TRANSFERS,
        defaults={
            "block_number": block_number,
            "last_update": datetime.now(),
        }
    )

    transaction_cursor, _ = NotifyCursor.objects.get_or_create(
        cursor_id=CursorId.TRANSACTIONS,
        defaults={
            "block_number": block_number,
            "last_update": datetime.now(),
        }
    )

    availible_kwargs_valgen = {
        "transfer_cursor": lambda: transfer_cursor,
        "transaction_cursor": lambda: transaction_cursor,
        "transactions": lambda: transactions(transaction_cursor.block_number),
        "new_transactions": lambda: transactions(
            transaction_cursor.block_number
        ),
        "transfers": lambda: transfers(0),
        "new_transfers": lambda: transfers(transfer_cursor.block_number),
        "logs": lambda: logs(0),
        "new_logs": lambda: logs(transfer_cursor.block_number),
    }

    for mod in mods:
        # Figure out the kwargs it wants
        func_spec = inspect.getfullargspec(mod.run_trigger)

        # Give it values
        script_kwargs = {
            k: availible_kwargs_valgen.get(k)() for k in func_spec.args
        }

        # Execute and save actions for return
        events.extend(mod.run_trigger(**script_kwargs))

    transfer_cursor.block_number = block_number
    transfer_cursor.last_update = datetime.now()
    transfer_cursor.save()

    transaction_cursor.block_number = block_number
    transaction_cursor.last_update = datetime.now()
    transaction_cursor.save()

    return events
