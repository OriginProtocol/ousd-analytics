import datetime
from decimal import Decimal
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.core.paginator import Paginator

from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.core.validators import validate_email

from django.views.decorators.csrf import csrf_exempt
import random
from django.template.loader import render_to_string

from django.db import connection
from django.db.models import Q
from core.blockchain.addresses import (
    DRIPPER,
    OUSD,
    OETH,
    USDT,
    STRAT3POOL,
    STRATCOMP,
    STRATAAVEDAI,
    STRATCONVEX1,
)
from core.blockchain.sigs import TRANSFER
from core.blockchain.const import (
    OUSD_CONTRACTS,
    START_OF_OUSD_V2,
    BLOCKS_PER_DAY,
    START_OF_OUSD_V2_TIME,
    report_stats,
    curve_report_stats,
)
from core.blockchain.harvest import reload_all, refresh_transactions, snap
from core.blockchain.harvest.blocks import ensure_block, ensure_day
from core.blockchain.harvest.snapshots import (
    ensure_asset,
    ensure_supply_snapshot,
    latest_snapshot,
    latest_snapshot_block_number,
    calculate_snapshot_data,
)
from core.blockchain.apy import get_trailing_apr, get_trailing_apy, to_apy
from core.blockchain.harvest.transactions import (
    get_internal_transactions,
    ensure_transaction_and_downstream,
)
from core.blockchain.harvest.transaction_history import (
    create_time_interval_report,
    create_time_interval_report_for_previous_week,
    create_time_interval_report_for_previous_month,
    calculate_report_change,
    send_report_email,
    get_history_for_address,
    _daily_rows
)

from core.blockchain.rpc import (
    balanceOf,
    dripper_available,
    dripper_drip_rate,
    latest_block,
    rebasing_credits_per_token,
    totalSupply,
    OUSDMetaStrategy
)

from core.channels.email import Email
from core.coingecko import get_price
from core.common import dict_append
from core.logging import get_logger
from core.models import (
    Log,
    SupplySnapshot,
    OgnStaked,
    TokenTransfer,
    AnalyticsReport,
    Transaction,
    Subscriber,
    OriginTokens
)
from core.forms import SubscriberForm
from django.conf import settings
import json

from core.blockchain.strategies import OUSD_STRATEGIES, OUSD_BACKING_ASSETS
from core.blockchain.strategies import OETH_STRATEGIES, OETH_BACKING_ASSETS

log = get_logger(__name__)


def fetch_assets(block_number, project=OriginTokens.OUSD):
    # These probably won't harvest since block_number comes from snapshots
    if project == OriginTokens.OUSD:
        dai = ensure_asset("DAI", block_number)
        usdt = ensure_asset("USDT", block_number)
        usdc = ensure_asset("USDC", block_number)
        ousd = ensure_asset("OUSD", block_number)
        lusd = ensure_asset("LUSD", block_number)
        return [dai, usdt, usdc, ousd, lusd]
    elif project == OriginTokens.OETH:
        weth = ensure_asset("WETH", block_number, OriginTokens.OETH)
        frxeth = ensure_asset("FRXETH", block_number, OriginTokens.OETH)
        reth = ensure_asset("RETH", block_number, OriginTokens.OETH)
        steth = ensure_asset("STETH", block_number, OriginTokens.OETH)
        oeth = ensure_asset("OETH", block_number, OriginTokens.OETH)
        return [weth, frxeth, reth, steth, oeth]
    return []


def dashboard(request):
    block_number = latest_snapshot_block_number()

    apy = get_trailing_apy(days=365)
    if apy < 0:
        apy = 0

    assets = fetch_assets(block_number)

    total_vault = sum(x.vault_holding for x in assets)
    total_aave = sum(x.aavestrat_holding for x in assets)
    total_compstrat = sum(x.compstrat_holding for x in assets)
    total_threepool = sum(x.threepoolstrat_holding for x in assets)
    total_assets = sum(x.total() for x in assets)
    total_supply = totalSupply(OUSD, 18, block_number)
    total_value = sum(x.redeem_value() for x in assets)
    extra_assets = (total_assets - total_supply) * Decimal(0.9)
    extra_value = total_value - total_supply

    logs_q = Log.objects.filter(address__in=OUSD_CONTRACTS)
    topic = request.GET.get("topic_0")
    if topic:
        logs_q = logs_q.filter(topic_0=topic)
    latest_logs = logs_q[:100]
    weekly_reports = AnalyticsReport.objects.filter(
        week__isnull=False,
        project=OriginTokens.OUSD
    ).order_by("-year", "-week")
    if (len(weekly_reports) > 0):
        token_holder_amount = weekly_reports[0].accounts_holding_ousd

    filters = [
        {
            "topic": "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef",
            "label": "transfers",
        },
        {
            "topic": "0x0f6798a560793a54c3bcfe86a93cde1e73087d944c0ea20544137d4121396885",
            "label": "mints",
        },
        {
            "topic": "0x222838db2794d11532d940e8dec38ae307ed0b63cd97c233322e221f998767a6",
            "label": "redeems",
        },
        {
            "topic": "0x09516ecf4a8a86e59780a9befc6dee948bc9e60a36e3be68d31ea817ee8d2c80",
            "label": "rebases",
        },
        {
            "topic": "0x712ae1383f79ac853f8d882153778e0260ef8f03b504e2866e0593e04d2b291f",
            "label": "governance",
        },
        {
            "topic": "0xd78ad95fa46c994b6551d0da85fc275fe613ce37657fb8d5e3d130840159d822",
            "label": "swaps",
        },
        {
            "topic": "0x47cee97cb7acd717b3c0aa1435d004cd5b3c8c57d70dbceb4e4458bbd60e39d4",
            "label": "claims",
        },
    ]

    stratconvex_address = STRATCONVEX1
    stratcomp_address = STRATCOMP
    strataavedai_address = STRATAAVEDAI

    ui_layout = _get_strat_layout(assets)

    return _cache(20, render(request, "dashboard.html", locals()))

def _get_strat_holdings(assets, project=OriginTokens.OUSD):
    all_strats = {}
    strat_config = OUSD_STRATEGIES if project == OriginTokens.OUSD else OETH_STRATEGIES
    backing_assets = OUSD_BACKING_ASSETS if project == OriginTokens.OUSD else OETH_BACKING_ASSETS

    for (strat_key, strat) in strat_config.items():
        total = 0
        holdings = []

        for asset in assets:
            if not asset.symbol in strat.get("SUPPORTED_ASSETS", backing_assets):
                continue
            balance = asset.get_strat_holdings(strat_key)
            holdings.append((asset.symbol, balance))
            total += balance

        all_strats[strat_key] = {
            "name": strat["NAME"],
            "address": strat["ADDRESS"],
            "icon_file": strat.get("ICON_NAME", "buffer-icon.svg"),
            "total": total,
            "holdings": holdings
        }

    return all_strats


def _get_strat_layout(assets):
    all_strats = _get_strat_holdings(assets)

    ui_layout = []

    # Rename vault car title
    vault_holdings = dict(all_strats["vault_holding"])
    vault_holdings["name"] = "Vault Holdings"

    # First row contains vault holdings and strategy allocations
    ui_layout.append([
        vault_holdings,
        {
            "name": "Vault Strategy Allocations",
            "icons": dict([(val["name"], val["icon_file"]) for key, val in all_strats.items()]),
            "holdings": sorted([(val["name"] if key != "vault_holding" else "Unallocated", val["total"]) for key, val in all_strats.items()],  key=lambda x: -x[1]),
        }
    ])

    del all_strats["vault_holding"]

    cols = 3
    strat_keys = list(all_strats.keys())
    rows = 1 + len(strat_keys) // cols

    for i in range(0, rows):
        start_index = i * cols
        end_index = start_index + cols
        ui_layout.append(
            [all_strats[key] for key in strat_keys[start_index:end_index]]
        )

    return ui_layout


def reload(request):
    latest = latest_block()
    reload_all(latest - 2)
    return HttpResponse("ok")


def make_monthly_report(request):
    if not settings.ENABLE_REPORTS:
        print("Reports disabled on this instance")
        return HttpResponse("ok")

    print("Make monthly report requested")
    do_only_transaction_analytics = (
        request.GET.get("only_tx_report", "false") == "true"
    )
    create_time_interval_report_for_previous_month(
        None, None, do_only_transaction_analytics
    )
    return HttpResponse("ok")


def make_weekly_report(request):
    if not settings.ENABLE_REPORTS:
        print("Reports disabled on this instance")
        return HttpResponse("ok")

    print("Make weekly report requested")
    do_only_transaction_analytics = (
        request.GET.get("only_tx_report", "false") == "true"
    )
    create_time_interval_report_for_previous_week(
        None, None, do_only_transaction_analytics
    )
    return HttpResponse("ok")


def make_specific_month_report(request, year, month):
    if not settings.ENABLE_REPORTS:
        print("Reports disabled on this instance")
        return HttpResponse("ok")

    do_only_transaction_analytics = (
        request.GET.get("only_tx_report", "false") == "true"
    )
    create_time_interval_report_for_previous_month(
        year, month, do_only_transaction_analytics
    )
    return HttpResponse("ok")


def make_specific_week_report(request, year, week):
    if not settings.ENABLE_REPORTS:
        print("Reports disabled on this instance")
        return HttpResponse("ok")

    do_only_transaction_analytics = (
        request.GET.get("only_tx_report", "false") == "true"
    )
    create_time_interval_report_for_previous_week(
        year, week, do_only_transaction_analytics
    )
    return HttpResponse("ok")


def remove_specific_month_report(request, month):
    if not settings.ENABLE_REPORTS:
        print("Reports disabled on this instance")
        return HttpResponse("ok")

    year = datetime.datetime.now().year
    report = AnalyticsReport.objects.get(month=month, year=year, project=OriginTokens.OUSD)
    report.delete()
    return HttpResponse("ok")


def remove_specific_week_report(request, week):
    if not settings.ENABLE_REPORTS:
        print("Reports disabled on this instance")
        return HttpResponse("ok")

    year = datetime.datetime.now().year
    report = AnalyticsReport.objects.get(week=week, year=year, project=OriginTokens.OUSD)
    report.delete()
    return HttpResponse("ok")


def take_snapshot(request):
    latest = latest_block()
    snap(latest - 2)
    return HttpResponse("ok")


def fetch_transactions(request):
    latest = latest_block()
    refresh_transactions(latest - 2)
    return HttpResponse("ok")


def apr_index(request, project):
    latest_block_number = latest_snapshot_block_number(project)
    project_name = project.upper()

    contract_address = OUSD if project == OriginTokens.OUSD else OETH
    try:
        num_rows = int(request.GET.get("rows", 30))
    except ValueError:
        num_rows = 30
    rows = _daily_rows(min(120, num_rows), latest_block_number, project)
    del num_rows
    apy = get_trailing_apy(project=project)
    apy_365 = get_trailing_apy(days=365, project=project)

    assets = fetch_assets(latest_block_number)
    total_assets = sum(x.total() for x in assets)
    total_supply = totalSupply(contract_address, 18, latest_block_number)
    extra_assets = (total_assets - total_supply) + dripper_available()
    return _cache(1 * 60, render(request, "apr_index.html", locals()))


def supply(request):
    [
        pools,
        totals_by_rebasing,
        other_rebasing,
        other_non_rebasing,
        s,
    ] = calculate_snapshot_data()
    rebasing_pools = [x for x in pools if x["is_rebasing"]]
    non_rebasing_pools = [x for x in pools if x["is_rebasing"] == False]
    # return _cache(30, render(request, "supply.html", locals()))
    return render(request, "supply.html", locals())


def dripper(request):
    dripper_usdt = balanceOf(USDT, DRIPPER, 6)
    dripper_available_usdt = dripper_available()
    rate = dripper_drip_rate()
    dripper_drip_rate_per_minute = dripper_drip_rate() * 60
    dripper_drip_rate_per_hour = dripper_drip_rate() * 60 * 60
    dripper_drip_rate_per_day = dripper_drip_rate() * 24 * 60 * 60
    return _cache(10, render(request, "dripper.html", locals()))

def public_dashboards(request):
    embed_panel_width = '100%'
    embed_panel_height = '100%'
    return _cache(10, render(request, "public_dashboards.html", locals()))


def dune_analytics(request):
    return render(request, "dune_analytics.html", locals())


def strategist(request):
    return render(request, "strategist.html", locals())


def strategist_creator(request):
    return render(request, "strategist_creator.html", locals())


def api_apr_trailing(request, project):
    try:
        apr = get_trailing_apr(project=project)
    except ObjectDoesNotExist: 
        apr = 0

    if apr < 0:
        apr = "0"
    apy = to_apy(Decimal(apr))
    if apy < 0:
        apy = 0
    response = JsonResponse({"apr": apr, "apy": apy})
    response.setdefault("Access-Control-Allow-Origin", "*")
    return _cache(120, response)


def api_apr_trailing_days(request, project, days):
    try:
        apr = get_trailing_apr(days=int(days), project=project)
    except ObjectDoesNotExist: 
        apr = 0

    if apr < 0:
        apr = "0"
    apy = to_apy(Decimal(apr), days=int(days))
    if apy < 0:
        apy = 0
    response = JsonResponse({"apr": apr, "apy": apy})
    response.setdefault("Access-Control-Allow-Origin", "*")
    return _cache(120, response)


def api_apr_history(request, project):
    # On OETH we miss some data 
    # File "eagleproject/core/blockchain/harvest/transactions.py", line 157, in get_rebase_log
    # ).order_by('-block_number')[:1].get()
    # Crashes with `core.models.Log.DoesNotExist: Log matching query does not exist.`
    try:
        apr = get_trailing_apr(project=project)
    except ObjectDoesNotExist:
        apr = 0
    if apr < 0:
        apr = "0"
    try:
        apy = get_trailing_apy(project=project)
    except ObjectDoesNotExist:
        apy = 0
    if apy < 0:
        apy = 0
    latest_block_number = latest_snapshot_block_number(project)
    days = _daily_rows(8, latest_block_number, project)
    response = JsonResponse(
        {
            "apr": apr,
            "apy": apy,
            "daily": [{"apy": x.apy} for x in days],
        }
    )
    response.setdefault("Access-Control-Allow-Origin", "*")
    return _cache(120, response)


def api_apr_trailing_history(request, days, project):
    rows = _daily_rows(90, latest_snapshot_block_number(project))
    response = JsonResponse(
        {
            "trailing_history": [{"day": x.block_time, "trailing_apy": get_trailing_apy(x.block_number, days)} for x in rows],
        }
    )
    response.setdefault("Access-Control-Allow-Origin", "*")
    return _cache(120, response)


def api_speed_test(request):
    return _cache(120, JsonResponse({"test": "test"}))


def api_ratios(request, project):
    s = latest_snapshot(project)
    response = JsonResponse(
        {
            "current_credits_per_token": s.rebasing_credits_per_token,
            "next_credits_per_token": Decimal(1.0) / s.rebasing_credits_ratio,
        }
    )
    response.setdefault("Access-Control-Allow-Origin", "*")
    return _cache(30, response)


def api_address_yield(request, address, project):
    address = address.lower()
    data = _address_transfers(address, project)
    response = JsonResponse(
        {
            "address": data["address"],
            "lifetime_yield": "{:.2f}".format(data["yield_balance"]),
        }
    )
    response.setdefault("Access-Control-Allow-Origin", "*")
    return response


def api_address(request, project):
    addresses = (
        TokenTransfer.objects.filter(block_time__gte=START_OF_OUSD_V2_TIME, project=project)
        .values("to_address")
        .distinct()
        .values_list("to_address", flat=True)
    )
    return JsonResponse(
        {
            "addresses": sorted(list(addresses)),
        }
    )


def active_stake_stats():
    """ Get stats of the active stakes grouped by duration """
    utc_now = datetime.datetime.now(tz=datetime.timezone.utc)

    """ Trying to do aggregate math and Withdraw inferences here.  This data is
    a dict of OgnStaked with user_address as key.  We should be able to filter
    out matured and withdrawn OgnStaked instances after collection using their
    maturity dates/blocks.
    Afterwards, we can put them all into buckets of 30, 90, 365 day running
    totals of active stakes.
    """
    user_aggreate = {}
    nonsense_users = []
    total_30 = 0
    total_90 = 0
    total_365 = 0

    all_stakes = OgnStaked.objects.order_by("block_time").all()

    for stake in all_stakes:
        dict_append(user_aggreate, stake.user_address, stake)

    # This is an expensive filter to remove withdrawn stakes
    for user_address in user_aggreate.keys():
        active_stakes = []
        running_total = 0

        for stake in user_aggreate[user_address]:
            if stake.is_staked:
                active_stakes.append(stake)
                running_total += stake.amount

            elif not stake.is_staked:
                matured_stakes = [
                    x
                    for x in active_stakes
                    if x.block_time + x.staked_duration < utc_now
                ]
                mature_so_far = sum([x.amount for x in matured_stakes])

                # Silencing this because it's a bad calc and annoying log message
                # if mature_so_far != stake.staked_amount:
                #     log.error(
                #         'Stakes make no sense!  Withdraw {} does not match '
                #         'previous stakes of {}. User: {}'.format(
                #             stake.staked_amount,
                #             mature_so_far,
                #             user_address,
                #         )
                #     )
                #     # If this happens, something is fucked
                #     nonsense_users.append(user_address)
                #     break

                # else:
                active_stakes = list(set(active_stakes) - set(matured_stakes))
                running_total -= mature_so_far

        user_aggreate[user_address] = active_stakes

    for address in nonsense_users:
        del user_aggreate[address]

    unique_addresses = user_aggreate.keys()

    # Now we need to bucket all active stakes
    for user_address in unique_addresses:
        for stake in user_aggreate[user_address]:
            if stake.staked_duration == datetime.timedelta(days=30):
                total_30 += stake.amount
            elif stake.staked_duration == datetime.timedelta(days=90):
                total_90 += stake.amount
            elif stake.staked_duration == datetime.timedelta(days=365):
                total_365 += stake.amount
            else:
                log.error(
                    "Unknown stake duration of {}. Excluding from "
                    "totals.".format(stake.staked_duration)
                )

    return {
        "userCount": len(unique_addresses),
        "stats": [
            {"duration": 30, "total_staked": total_30},
            {"duration": 90, "total_staked": total_90},
            {"duration": 365, "total_staked": total_365},
        ],
    }


def address(request, address, project):
    address = address.lower()
    data = _address_transfers(address, project)
    data["project"] = project.upper()
    return render(request, "address.html", data)


def _address_transfers(address, project):
    long_address = address.replace("0x", "0x000000000000000000000000")
    latest_block_number = latest_snapshot_block_number(project)
    contract_address = OUSD if project == OriginTokens.OUSD else OETH
    # We want to avoid the case where the listener hasn't picked up a
    # transactions yet, but the user's balance has increased or decreased
    # due to a transfer. This would make a hugely wrong lifetime earned amount
    #
    # We refresh the DB every minute, so we will do two minutes worth of
    # blocks - conservatively 120 / 10 = 12 blocks.
    block_number = latest_block_number - 12
    transfers = (
        Log.objects.filter(address=contract_address, topic_0=TRANSFER)
        .filter(Q(topic_1=long_address) | Q(topic_2=long_address))
        .filter(block_number__gte=START_OF_OUSD_V2)
        .filter(block_number__lte=block_number)
    )
    transfers_in = sum(
        [x.ousd_value() for x in transfers if x.topic_2 == long_address]
    )
    transfers_out = sum(
        [x.ousd_value() for x in transfers if x.topic_1 == long_address]
    )
    current_balance = balanceOf(contract_address, address, 18, block=block_number)
    non_yield_balance = transfers_in - transfers_out
    yield_balance = current_balance - non_yield_balance
    return {
        "address": address,
        "transfers": transfers,
        "transfers_in": transfers_in,
        "transfers_out": transfers_out,
        "current_balance": current_balance,
        "non_yield_balance": non_yield_balance,
        "yield_balance": yield_balance,
    }


def _my_assets(address, block_number):
    dai = ensure_asset("DAI", block_number)
    usdt = ensure_asset("USDT", block_number)
    usdc = ensure_asset("USDC", block_number)
    total_supply = totalSupply(OUSD, 18, block_number)

    current_balance = balanceOf(OUSD, address, 18, block_number)
    total_supply = totalSupply(OUSD, 18, block_number)

    return {
        "my": {
            "DAI": (dai.vault_holding + dai.compstrat_holding)
            * current_balance
            / total_supply,
            "USDC": (usdc.vault_holding + usdc.compstrat_holding)
            * current_balance
            / total_supply,
            "USDT": (usdt.vault_holding + usdt.compstrat_holding)
            * current_balance
            / total_supply,
        },
        "current_balance": current_balance,
        "total_supply": total_supply,
    }


# def test_email(request):
#     weekly_reports = AnalyticsReport.objects.filter(week__isnull=False).order_by("-year", "-week")
#     send_report_email("OUSD", 'Weekly report', weekly_reports[0], weekly_reports[1], "Weekly")
#     return HttpResponse("ok")
    

def api_address_history(request, address, project=OriginTokens.OUSD):
    page_number = request.GET.get("page", 1)
    per_page = request.GET.get("per_page", 50)
    transaction_filter = request.GET.get("filter")
    history = get_history_for_address(address, transaction_filter, project=project)
    paginator = Paginator(history, per_page)
    page_obj = paginator.get_page(page_number)
    pages = paginator.num_pages
    response = JsonResponse(
        {
            "page": {
                "current": page_obj.number,
                "pages": pages,
                "filters": []
                if transaction_filter == None
                else transaction_filter.split(),
            },
            "history": page_obj.object_list,
        }
    )
    response.setdefault("Access-Control-Allow-Origin", "*")
    return response


def strategies(request, project=OriginTokens.OUSD):
    block_number = latest_snapshot_block_number(project)
    assets = fetch_assets(block_number, project)

    all_strats = _get_strat_holdings(assets, project=project)

    # Returns an object with UUID as keys when set, otherwise returns an array
    structured = project == OriginTokens.OETH or request.GET.get("structured") is not None

    for (key, strat) in all_strats.items():
        holdings = {}
        for (asset, holding) in strat["holdings"]:
            holdings[asset] = float(holding or 0)
        strat["total"] = float(strat["total"] or 0)
        strat["holdings"] = holdings

    if structured is None:
        # TODO: Backward compatibility, remove after making sure that every repo has been updated
        all_strats = [{
            "name": strat["name"],
            "total": strat["total"],
            "dai": strat["holdings"].get("DAI"),
            "usdt": strat["holdings"].get("USDT"),
            "usdc": strat["holdings"].get("USDC"),
            "ousd": strat["holdings"].get("OUSD"),
            "lusd": strat["holdings"].get("LUSD"),
        } for (strat_key, strat) in all_strats.items()]

    response = JsonResponse({
        "strategies": all_strats
    })
    response.setdefault("Access-Control-Allow-Origin", "*")
    return _cache(120, response)


def collateral(request, project):
    block_number = latest_snapshot_block_number(project=project)
    assets = fetch_assets(block_number, project=project)
    collateral = []
    for asset in assets:
        collateral.append({"name": asset.symbol.lower(), "total": asset.total()})
    response = JsonResponse(
        {
            "collateral": collateral
        }
    )
    response.setdefault("Access-Control-Allow-Origin", "*")
    return _cache(120, response)


def _get_previous_report(report, all_reports=None):
    is_monthly = report.month is not None

    if is_monthly:
        all_reports = (
            all_reports
            if all_reports is not None
            else AnalyticsReport.objects.filter(month__isnull=False, project=OriginTokens.OUSD).order_by(
                "-year", "-month"
            )
        )
        prev_year = report.year - 1 if report.month == 1 else report.year
        prev_month = 12 if report.month == 1 else report.month - 1
        prev_report = list(
            filter(
                lambda report: report.month == prev_month
                and report.year == prev_year,
                all_reports,
            )
        )
        return prev_report[0] if len(prev_report) > 0 else None
    else:
        all_reports = (
            all_reports
            if all_reports is not None
            else AnalyticsReport.objects.filter(week__isnull=False, project=OriginTokens.OUSD).order_by(
                "-year", "-week"
            )
        )
        prev_year = report.year - 1 if report.week == 0 else report.year
        prev_week = 53 if report.week == 0 else report.week - 1
        prev_report = list(
            filter(
                lambda report: report.week == prev_week
                and report.year == prev_year,
                all_reports,
            )
        )
        return prev_report[0] if len(prev_report) > 0 else None


def report_monthly(request, year, month):
    report = AnalyticsReport.objects.filter(month=month, year=year, project=OriginTokens.OUSD)[0]
    prev_report = _get_previous_report(report)
    stats = report_stats
    stat_keys = stats.keys()
    curve_stats = curve_report_stats
    curve_stat_keys = curve_stats.keys()
    is_monthly = True
    change = calculate_report_change(report, prev_report)
    report.transaction_report = json.loads(str(report.transaction_report))
    latest = year == datetime.datetime.now().year and month == int(datetime.datetime.now().strftime("%m")) - 1
    if month == 12:
        next_month = 0
        next_year = year + 1
    else:
        next_month = month + 1
        next_year = year
    return render(request, "analytics_report.html", locals())


def report_weekly(request, year, week):
    report = AnalyticsReport.objects.filter(week=week, year=year)[0]
    prev_report = _get_previous_report(report)
    stats = report_stats
    stat_keys = stats.keys()
    curve_stats = curve_report_stats
    curve_stat_keys = curve_stats.keys()
    is_monthly = False
    change = calculate_report_change(report, prev_report)
    report.transaction_report = json.loads(str(report.transaction_report))
    latest = year == datetime.datetime.now().year and week == int(datetime.datetime.now().strftime("%W")) - 1
    if week == 51:
        next_week = 0
        next_year = year + 1
    else:
        next_week = week + 1
        next_year = year

    return render(request, "analytics_report.html", locals())


def report_latest_weekly(request):
    year = datetime.datetime.now().year
    week = int(datetime.datetime.now().strftime("%W")) - 1
    return redirect("weekly", year, week)


def reports(request):
    monthly_reports = AnalyticsReport.objects.filter(
        month__isnull=False,
        project=OriginTokens.OUSD
    ).order_by("-year", "-month")
    weekly_reports = AnalyticsReport.objects.filter(
        week__isnull=False,
        project=OriginTokens.OUSD
    ).order_by("-year", "-week")
    stats = report_stats
    stat_keys = stats.keys()

    enriched_monthly_reports = []
    for monthly_report in monthly_reports:
        prev_report = _get_previous_report(monthly_report, monthly_reports)
        monthly_report.transaction_report = json.loads(
            str(monthly_report.transaction_report)
        )
        enriched_monthly_reports.append(
            (
                monthly_report,
                calculate_report_change(monthly_report, prev_report),
            )
        )

    enriched_weekly_reports = []
    for weekly_report in weekly_reports:
        prev_report = _get_previous_report(weekly_report, weekly_reports)
        weekly_report.transaction_report = json.loads(
            str(weekly_report.transaction_report)
        )
        enriched_weekly_reports.append(
            (
                weekly_report,
                calculate_report_change(weekly_report, prev_report),
            )
        )

    return render(request, "analytics_reports.html", locals())


def generate_token():
    return "%0.12d" % random.randint(0, 999999999999)


@csrf_exempt
def subscribe(request):
    latest_report_url = request.build_absolute_uri('/reports/weekly')

    project = request.POST['project'] or OriginTokens.OUSD
    
    if request.method == 'POST':
        sub = Subscriber.objects.filter(email=request.POST['email'],project=project).first()
        if sub and sub.confirmed is True and sub.unsubscribed is False:
            action = 'exists'
        else:
            try:
                validate_email(request.POST['email'])
            except ValidationError as e:
                return render(request, 'subscription.html', {'action': 'invalid', 'form': SubscriberForm(), 'latest_report': latest_report_url})
            else:
                if not sub:
                    sub = Subscriber(email=request.POST['email'], project=project, conf_num=generate_token())
                    sub.save()
                    
                summary = 'OUSD Analytics Report Confirmation'
                e = Email(summary, render_to_string('subscription_confirmation.html', {
                    'uri': request.build_absolute_uri('/reports/confirm'),
                    'email': sub.email,
                    'conf_num': sub.conf_num,
                }))
                result = e.execute([sub.email])
                action = 'added'

        return render(request, 'subscription.html', {'email': sub.email, 'action': action, 'form': SubscriberForm()})
    else:
        return render(request, 'subscription.html', {'form': SubscriberForm()})


def confirm(request):
    try:
        email = request.GET['email']
        conf_num = request.GET['conf_num']
        sub = Subscriber.objects.get(email=email,conf_num=conf_num)

        sub.confirmed = True
        sub.unsubscribed = False
        sub.save()
        return render(request, 'subscription.html', {'email': sub.email, 'action': 'confirmed'})
    except:
        return render(request, 'subscription.html', {'action': 'denied'})


def unsubscribe(request):
    try:
        email = request.GET['email']
        conf_num = request.GET['conf_num']
        sub = Subscriber.objects.get(email=email,conf_num=conf_num)
        sub.unsubscribed = True
        sub.save()
        return render(request, 'subscription.html', {'email': sub.email, 'action': 'unsubscribed'})
    except:
        return render(request, 'subscription.html', {'action': 'denied'})

def backfill_internal_transactions(request):
    transactions = Transaction.objects.filter(internal_transactions={})[:6000]
    total = len(transactions)
    print("All transactions:", total)
    count = 0
    for transaction in transactions:
        count += 1
        print(
            "DOING THIS TRANSACTION {} on {} and {} to go".format(
                transaction.tx_hash, count, total - count
            )
        )
        transaction.internal_transactions = get_internal_transactions(
            transaction.tx_hash
        )
        transaction.save()

    return HttpResponse("ok")


def tx_debug(request, tx_hash):
    transaction = ensure_transaction_and_downstream(tx_hash)
    logs = Log.objects.filter(transaction_hash=tx_hash)
    return _cache(1200, render(request, "debug_tx.html", locals()))


def _cache(seconds, response):
    response.setdefault("Cache-Control", "public, max-age=%d" % seconds)
    response.setdefault("Vary", "Accept-Encoding")
    return response





def staking_stats(request, project):
    data = active_stake_stats()

    return JsonResponse(
        {
            "success": True,
            "userCount": data["userCount"],
            "lockupSum": sum(row["total_staked"] for row in data["stats"]),
        }
    )


def staking_stats_by_duration(request, project):
    data = active_stake_stats()
    stats = data["stats"]

    return JsonResponse(
        {
            "success": True,
            "data": [
                [row["duration"], float(row["total_staked"])] for row in stats
            ],
        }
    )


def coingecko_pools(request, project):
    """ API for CoinGecko to consume to get details about OUSD and OGN """
    ousd_liquidity = totalSupply(OUSD, 18)
    ousd_apy = get_trailing_apy()
    ogn_stats_data = active_stake_stats()
    ogn_stats = ogn_stats_data["stats"]
    ogn_30_liquidity = 0
    ogn_90_liquidity = 0
    ogn_365_liquidity = 0

    for stat in ogn_stats:
        if stat["duration"] == 30:
            ogn_30_liquidity = stat["total_staked"]
        elif stat["duration"] == 90:
            ogn_90_liquidity = stat["total_staked"]
        elif stat["duration"] == 365:
            ogn_365_liquidity = stat["total_staked"]

    ousd_price = get_price("OUSD").get("usd", 0)
    ogn_price = get_price("OGN").get("usd", 0)

    log.debug("CoinGecko OUSD Price: {}".format(ousd_price))
    log.debug("CoinGecko OGN Price: {}".format(ogn_price))

    return _cache(
        60,
        JsonResponse(
            [
                {
                    "identifier": "OUSD Vault",
                    "liquidity_locked": float(ousd_liquidity) * ousd_price,
                    "apy": ousd_apy,
                },
                {
                    "identifier": "OGN 30-day Staking",
                    "liquidity_locked": float(ogn_30_liquidity) * ogn_price,
                    "apy": 7.5,
                },
                {
                    "identifier": "OGN 90-day Staking",
                    "liquidity_locked": float(ogn_90_liquidity) * ogn_price,
                    "apy": 12.5,
                },
                {
                    "identifier": "OGN 365-day Staking",
                    "liquidity_locked": float(ogn_365_liquidity) * ogn_price,
                    "apy": 25.0,
                },
            ],
            safe=False,
        ),
    )
