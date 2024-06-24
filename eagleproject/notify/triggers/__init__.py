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
import os
from pathlib import Path
from datetime import datetime, timedelta, timezone
from importlib import import_module
from django.db.models import Max

from core.logging import get_logger
from core.models import (
    AssetBlock,
    AaveLendingPoolCoreSnapshot,
    CTokenSnapshot,
    Block,
    Log,
    OgnStakingSnapshot,
    OracleSnapshot,
    TokenTransfer,
    StoryStakingSnapshot,
    SupplySnapshot,
    Transaction,
    OriginTokens,
)
from notify.models import CursorId, NotifyCursor
from notify.events import event_high

from core.blockchain.const import START_OF_OETH

log = get_logger(__name__)

ME = Path(__file__).resolve()
THIS_DIR = ME.parent
ONLY_RUN_TRIGGER = os.environ.get("ONLY_RUN_TRIGGER")
SKIP_TRIGGERS = [
    "noop",
    # TODO: Maybe add these back when Aave v2 snapshots added
    "aave_lpc_supply_rates",
    "aave_lpc_total_liquidity",
    # NOTE: Removing this since for some reason they seem to spam Discord notifications.
    # Also, with the new Prometheus monitoring system, this is redundant
    "assetblock_holdings",

    "ctoken_totalsupply",
    "ctoken_supplyrates",
    "ctoken_totalborrows",

]
log = logging.getLogger("notify.triggers")


def strip_ext(fname):
    """ Strip an extension from a filename """
    if "." not in fname:
        return fname
    return ".".join(fname.split(".")[:-1])


def load_triggers(project = OriginTokens.OUSD):
    """ Loads all trigger modules in this dir """

    if ONLY_RUN_TRIGGER is not None:
        triggers = ONLY_RUN_TRIGGER.split(",")
        return [
            import_module("notify.triggers.{}".format(trigger))
            for trigger in triggers
        ]

    files = [
        x
        for x in THIS_DIR.iterdir()
        if (
            x.is_file()
            and x.name.endswith(".py")
            and not x.name.startswith("__")
        )
    ]

    if project == OriginTokens.OETH:
        files = [
            x
            for x in files
            if not (
                x.name.startswith("aave_")
                or x.name.startswith("compound_")
                or x.name.startswith("ctoken_")
                or x.name.startswith("curve_")
                or x.name.startswith("story_")
                or x.name.startswith("staking_")
                or x.name.startswith("series_")
                or x.name.startswith("feevault_")
            )
        ]

    return [
        import_module("notify.triggers.{}".format(strip_ext(mod.name)))
        for mod in files
        if strip_ext(mod.name) not in SKIP_TRIGGERS
    ]


def transfers(block_number, project=OriginTokens.OUSD):
    """ Get all transfers since given block """
    return TokenTransfer.objects.filter(tx_hash__block_number__gt=block_number, project=project)


def transactions(block_number):
    """ Get all transactions since given block """
    return Transaction.objects.filter(block_number__gt=block_number)


def logs(block_number):
    """ Get all event logs since given block """
    return Log.objects.filter(block_number__gt=block_number).order_by(
        "block_number", "transaction_index", "log_index"
    )


def latest_ogn_staking_snap():
    try:
        return OgnStakingSnapshot.objects.all().order_by("-block_number")[0]
    except Exception as e:
        log.error(str(e))
        return None


def oracles_snaps(block_number):
    return OracleSnapshot.objects.filter(block_number=block_number)


def ctoken_snapshots(block_number):
    return CTokenSnapshot.objects.filter(block_number=block_number)


def recent_ctoken_snapshots(snap_count=5):
    """ Get the latest N snapshots for all cTokens """
    return CTokenSnapshot.objects.filter(
        block_number__in=CTokenSnapshot.objects.order_by("-block_number")
        .values("block_number")
        .distinct()[:snap_count]
    ).order_by("-block_number", "address")


def recent_aave_reserve_snapshots(snap_count=5):
    return AaveLendingPoolCoreSnapshot.objects.filter(
        block_number__in=AaveLendingPoolCoreSnapshot.objects.order_by(
            "-block_number"
        )
        .values("block_number")
        .distinct()[:snap_count]
    ).order_by("-block_number", "asset")


def aave_reserve_snapshots(block_number):
    return AaveLendingPoolCoreSnapshot.objects.filter(block_number=block_number)


def past_asset_blocks(
    after=datetime.now() - timedelta(days=7), 
    until_block=None,
    project=OriginTokens.OUSD
):
    """ Get previous asset blocks after `after` """
    try:
        first_block_after = Block.objects.filter(
            block_time__gte=after
        ).order_by("block_number")[0]
    except IndexError:
        return []

    ablocks = AssetBlock.objects.filter(
        block_number__gte=first_block_after.block_number,
        project=project,
    )

    if until_block:
        ablocks = ablocks.filter(block_number__lt=until_block)

    return ablocks.order_by("block_number")


def latest_asset_blocks(after_block_number, project=OriginTokens.OUSD):
    """ Get previous asset blocks after `after_block_number` """
    return AssetBlock.objects.filter(
        block_number__gt=after_block_number,
        project=project,
    ).order_by("block_number")


def latest_story_snapshots(limit=2):
    """ Get the last N amount of story snapshots """
    return StoryStakingSnapshot.objects.order_by("-block_number")[:limit]


def run_all_triggers():
    """ Run all triggers """
    events = []

    for project in [OriginTokens.OUSD, OriginTokens.OETH]:
        mods = load_triggers(project=project)
        
        is_ousd = project == OriginTokens.OUSD
        start_block_number = 0 if is_ousd else START_OF_OETH

        # Source from the DB to prevent a race with data collection
        max_block = Block.objects.all().aggregate(Max("block_number"))
        max_snapshot_block = SupplySnapshot.objects.filter(project=project).aggregate(
            Max("block_number")
        )
        block_number = start_block_number
        snapshot_block_number = start_block_number

        if max_block:
            block_number = max_block.get("block_number__max", 0)
        if max_snapshot_block:
            snapshot_block_number = max_snapshot_block.get("block_number__max", 0)

        transfer_cursor, _ = NotifyCursor.objects.get_or_create(
            cursor_id=CursorId.TRANSFERS if is_ousd else CursorId.OETH_TRANSFERS,
            project=project,
            defaults={
                "block_number": block_number,
                "last_update": datetime.now(tz=timezone.utc),
            },
        )

        transaction_cursor, _ = NotifyCursor.objects.get_or_create(
            cursor_id=CursorId.TRANSACTIONS if is_ousd else CursorId.OETH_TRANSACTIONS,
            project=project,
            defaults={
                "block_number": block_number,
                "last_update": datetime.now(tz=timezone.utc),
            },
        )

        snapshot_cursor, _ = NotifyCursor.objects.get_or_create(
            cursor_id=CursorId.SNAPSHOT if is_ousd else CursorId.OETH_SNAPSHOT,
            project=project,
            defaults={
                "block_number": snapshot_block_number,
                "last_update": datetime.now(tz=timezone.utc),
            },
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
            "transfers": lambda: transfers(start_block_number, project=project),
            "new_transfers": lambda: transfers(transfer_cursor.block_number, project=project),
            "logs": lambda: logs(start_block_number),
            "new_logs": lambda: logs(transaction_cursor.block_number),
            "ogn_staking_snapshot": latest_ogn_staking_snap,
            "oracle_snapshots": lambda: oracles_snaps(snapshot_block_number),
            "ctoken_snapshots": lambda: ctoken_snapshots(snapshot_block_number),
            "recent_ctoken_snapshots": lambda: recent_ctoken_snapshots(),
            "aave_reserve_snapshots": lambda: aave_reserve_snapshots(
                snapshot_block_number
            ),
            "recent_aave_reserve_snapshots": lambda: recent_aave_reserve_snapshots(),
            "latest_asset_blocks": lambda: latest_asset_blocks(
                snapshot_cursor.block_number,
                project=project
            ),
            "last_week_asset_blocks": lambda: past_asset_blocks(
                until_block=snapshot_cursor.block_number,
                project=project
            ),
            "latest_story_snapshots": lambda: latest_story_snapshots,
        }

        for mod in mods:
            # Figure out the kwargs it wants
            func_spec = inspect.getfullargspec(mod.run_trigger)

            # Give it values
            script_kwargs = {
                k: availible_kwargs_valgen[k]() for k in func_spec.args
            }

            try:
                log.debug(f"Executing trigger: {mod.__name__}")
                # Execute and save actions for return
                events.extend(mod.run_trigger(**script_kwargs))
            except Exception as e:
                log.exception("Exception occurred running trigger")
                log.exception(e)
                events.extend([
                    event_high("{} Trigger Failed for Block {}".format(mod.__name__, block_number), str(e))
                ])

        if transfer_cursor.block_number != block_number:
            transfer_cursor.block_number = block_number
            transfer_cursor.last_update = datetime.now(tz=timezone.utc)
            transfer_cursor.save()

        if transaction_cursor.block_number != block_number:
            transaction_cursor.block_number = block_number
            transaction_cursor.last_update = datetime.now(tz=timezone.utc)
            transaction_cursor.save()

        if snapshot_cursor.block_number != snapshot_block_number:
            snapshot_cursor.block_number = snapshot_block_number
            snapshot_cursor.last_update = datetime.now(tz=timezone.utc)
            snapshot_cursor.save()

    events.sort()

    return events
