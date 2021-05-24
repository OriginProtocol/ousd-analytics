import datetime
from decimal import Decimal
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.db import connection
from django.db.models import Q
from core.blockchain.addresses import (
    OUSD,
    USDT,
    OUSD_USDT_UNISWAP,
    OUSD_USDT_SUSHI,
    COMPENSATION_CLAIMS,
    STRAT3POOL,
    STRATCOMP,
    STRATAAVEDAI,
)
from core.blockchain.sigs import TRANSFER
from core.blockchain.const import (
    OUSD_CONTRACTS,
    START_OF_OUSD_V2,
)
from core.blockchain.harvest import reload_all, refresh_transactions, snap
from core.blockchain.harvest.snapshots import (
    ensure_asset,
    ensure_supply_snapshot,
)
from core.blockchain.harvest.transactions import (
    ensure_transaction_and_downstream,
)
from core.blockchain.rpc import (
    balanceOf,
    latest_block,
    rebasing_credits_per_token,
    totalSupply,
)
from core.coingecko import get_price
from core.common import dict_append
from core.logging import get_logger
from core.models import Log, SupplySnapshot, OgnStaked

log = get_logger(__name__)

BLOCKS_PER_DAY = 6500


def dashboard(request):
    block_number = _latest_snapshot_block_number()

    # These probably won't harvest since block_number comes from snapshots
    dai = ensure_asset("DAI", block_number)
    usdt = ensure_asset("USDT", block_number)
    usdc = ensure_asset("USDC", block_number)
    comp = ensure_asset("COMP", block_number)

    apy = _get_trailing_apy()

    assets = [dai, usdt, usdc]
    total_vault = sum(x.vault_holding for x in assets)
    total_aave = sum(x.aavestrat_holding for x in assets)
    total_compstrat = sum(x.compstrat_holding for x in assets)
    total_threepool = sum(x.threepoolstrat_holding for x in assets)
    total_assets = sum(x.total() for x in assets)
    total_comp = comp.total()
    total_supply = totalSupply(OUSD, 18, block_number)
    total_value = sum(x.redeem_value() for x in assets)
    extra_assets = (total_assets - total_supply) * Decimal(0.9)
    extra_value = total_value - total_supply

    logs_q = Log.objects.filter(address__in=OUSD_CONTRACTS)
    topic = request.GET.get("topic_0")
    if topic:
        logs_q = logs_q.filter(topic_0=topic)
    latest_logs = logs_q[:100]

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
            "topic": "0x99e56f783b536ffacf422d59183ea321dd80dcd6d23daa13023e8afea38c3df1",
            "label": "rebases",
        },
        {
            "topic": "0xa560e3198060a2f10670c1ec5b403077ea6ae93ca8de1c32b451dc1a943cd6e7",
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

    strat3pool_address = STRAT3POOL
    stratcomp_address = STRATCOMP
    strataavedai_address = STRATAAVEDAI

    return _cache(20, render(request, "dashboard.html", locals()))


def reload(request):
    latest = latest_block()
    reload_all(latest - 2)
    # Disable the reach-back for the time being
    # reload_all(latest - 2 - BLOCKS_PER_DAY * 7)  # Week ago, for APR
    return HttpResponse("ok")


def take_snapshot(request):
    latest = latest_block()
    snap(latest - 2)
    return HttpResponse("ok")


def fetch_transactions(request):
    latest = latest_block()
    refresh_transactions(latest - 2)
    return HttpResponse("ok")


def apr_index(request):
    latest_block_number = _latest_snapshot_block_number()
    rows = _daily_rows(30, latest_block_number)
    seven_day_apy = _get_trailing_apy()
    return _cache(5 * 60, render(request, "apr_index.html", locals()))


def supply(request):
    pools_config = [
        ("Uniswap OUSD/USDT", OUSD_USDT_UNISWAP, False),
        ("Sushi OUSD/USDT", OUSD_USDT_SUSHI, False),
        ("OUSD Compensation", COMPENSATION_CLAIMS, False),
    ]
    pools = []
    totals_by_rebasing = {True: Decimal(0), False: Decimal(0)}
    for name, address, is_rebasing in pools_config:
        amount = balanceOf(OUSD, address, 18)
        pools.append(
            {
                "name": name,
                "amount": amount,
                "is_rebasing": is_rebasing,
            }
        )
        totals_by_rebasing[is_rebasing] += amount
    pools = sorted(pools, key=lambda pool: 0-pool["amount"])

    s = _latest_snapshot()
    other_rebasing = s.rebasing_reported_supply() - totals_by_rebasing[True]
    other_non_rebasing = s.non_rebasing_reported_supply() - totals_by_rebasing[False]

    return _cache(30, render(request, "supply.html", locals()))

def flipper(request):
    return render(request, "flipper.html", locals())


def api_apr_trailing(request):
    apr = _get_trailing_apr()
    if apr < 0:
        apr = "0"
    apy = _get_trailing_apy()
    if apy < 0:
        apy = 0
    response = JsonResponse({"apr": apr, "apy": apy})
    response.setdefault("Access-Control-Allow-Origin", "*")
    return _cache(120, response)

def api_apr_history(request):
    apr = _get_trailing_apr()
    if apr < 0:
        apr = "0"
    apy = _get_trailing_apy()
    if apy < 0:
        apy = 0
    latest_block_number = _latest_snapshot_block_number()
    days = _daily_rows(8, latest_block_number)
    response = JsonResponse({
        "apr": apr,
        "apy": apy,
        "daily": [{'apy':x.apy} for x in days],
        })
    response.setdefault("Access-Control-Allow-Origin", "*")
    return _cache(120, response)


def api_speed_test(request):
    return _cache(120, JsonResponse({"test": "test"}))


def api_ratios(request):
    s = _latest_snapshot()
    response = JsonResponse({
        "current_credits_per_token": s.rebasing_credits_per_token,
        "next_credits_per_token": Decimal(1.0) / s.rebasing_credits_ratio,
    })
    response.setdefault("Access-Control-Allow-Origin", "*")
    return _cache(30, response)


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

    all_stakes = OgnStaked.objects.order_by('block_time').all()

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

                if mature_so_far != stake.staked_amount:
                    log.error(
                        'Stakes make no sense!  Withdraw {} does not match '
                        'previous stakes of {}. User: {}'.format(
                            stake.staked_amount,
                            mature_so_far,
                            user_address,
                        )
                    )
                    # If this happens, something is fucked
                    nonsense_users.append(user_address)
                    break

                else:
                    active_stakes = list(set(active_stakes) - set(matured_stakes))
                    running_total -= mature_so_far

        user_aggreate[user_address] = active_stakes

    for address in nonsense_users:
        del user_aggreate[address]

    # Now we need to bucket all active stakes
    for user_address in user_aggreate.keys():
        for stake in user_aggreate[user_address]:
            if stake.staked_duration == datetime.timedelta(days=30):
                total_30 += stake.amount
            elif stake.staked_duration == datetime.timedelta(days=90):
                total_90 += stake.amount
            elif stake.staked_duration == datetime.timedelta(days=365):
                total_365 += stake.amount
            else:
                log.error(
                    'Unknown stake duration of {}. Excluding from '
                    'totals.'.format(
                        stake.staked_duration
                    )
                )

    return [
        {'duration': 30, 'total_staked': total_30},
        {'duration': 90, 'total_staked': total_90},
        {'duration': 365, 'total_staked': total_365},
    ]


def address(request, address):
    if address != address.lower():
        return redirect("address", address=address.lower())
    long_address = address.replace("0x", "0x000000000000000000000000")
    latest_block_number = _latest_snapshot_block_number()
    transfers = (Log.objects
        .filter(address=OUSD, topic_0=TRANSFER)
        .filter(Q(topic_1=long_address) | Q(topic_2=long_address))
        .filter(block_number__gte=START_OF_OUSD_V2)
    )
    transfers_in = sum([
        x.ousd_value()
        for x in transfers
        if x.topic_2 == long_address
    ])
    transfers_out = sum(
        [x.ousd_value() for x in transfers if x.topic_1 == long_address]
    )
    current_balance = balanceOf(OUSD, address, 18)
    non_yield_balance = transfers_in - transfers_out
    yield_balance = current_balance - non_yield_balance
    return render(request, "address.html", locals())


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


def tx_debug(request, tx_hash):
    transaction = ensure_transaction_and_downstream(tx_hash)
    logs = Log.objects.filter(transaction_hash=tx_hash)
    return _cache(1200, render(request, "debug_tx.html", locals()))


def powermint(request):
    ousd_uniswap = balanceOf(OUSD, OUSD_USDT_UNISWAP, 18)
    usdt_uniswap = balanceOf(USDT, OUSD_USDT_UNISWAP, 6)
    eth_usd = 1780
    apr = Decimal(_get_trailing_apr())
    current_gas_price = 150
    return render(request, "powermint.html", locals())


def _cache(seconds, response):
    response.setdefault("Cache-Control", "public, max-age=%d" % seconds)
    response.setdefault("Vary", "Accept-Encoding")
    return response


def _latest_snapshot():
    return SupplySnapshot.objects.order_by("-block_number")[0]


def _latest_snapshot_block_number():
    return _latest_snapshot().block_number


def _daily_rows(steps, latest_block_number):
    STEP = BLOCKS_PER_DAY
    end_block_number = latest_block_number - (latest_block_number % STEP)
    block_numbers = list(
        range(end_block_number - (steps) * STEP, end_block_number + 1, STEP)
    ) + [latest_block_number]
    rows = []
    last_snapshot = None

    for block_number in block_numbers:
        if block_number < START_OF_OUSD_V2:
            continue
        s = ensure_supply_snapshot(block_number)
        if last_snapshot:
            blocks = s.block_number - last_snapshot.block_number
            change = (
                s.rebasing_credits_ratio / last_snapshot.rebasing_credits_ratio
            ) - Decimal(1)
            s.apr = Decimal(100) * change * (Decimal(365) * BLOCKS_PER_DAY) / blocks
            s.apy = _to_apy(s.apr, 1)
            s.unboosted = _to_apy((s.computed_supply - s.non_rebasing_supply) / s.computed_supply * s.apr, 1)
            s.gain = change * (s.computed_supply - s.non_rebasing_supply)
        rows.append(s)
        last_snapshot = s
    rows.reverse()
    # drop last row with incomplete information
    rows = rows[:-1]
    return rows

PREV_APR = None


def _get_trailing_apr():
    """
    Calculates the APR by using the OUSD rebase ratio. 

    This has the upside that it's simple to calculate and exactly matches 
    user's balance changes. 

    It has the downside that the number it pulls from only gets updated
    on rebases, making this method less acurate. It's bit iffy using it
    on only one day, but that's the data we have at the moment.
    """
    days = 7.00

    # Check cache first
    global PREV_APR
    if PREV_APR:
        good_to, apr = PREV_APR
        if good_to > datetime.datetime.today():
            return apr

    # Calculate
    block = _latest_snapshot_block_number()
    current = rebasing_credits_per_token(block)
    past = rebasing_credits_per_token(int(block - BLOCKS_PER_DAY * days))
    ratio = Decimal(float(past) / float(current))
    apr = ((ratio - Decimal(1)) * Decimal(100) * Decimal(365.25) / Decimal(days))

    # Save to cache
    good_to = datetime.datetime.today() + datetime.timedelta(minutes=5)
    PREV_APR = [good_to, apr]
    return apr


def _get_trailing_apy():
    apr = Decimal(_get_trailing_apr())
    apy = _to_apy(apr, 7.0)
    return round(apy, 2)

def _to_apy(apr, days):
    periods_per_year = Decimal(365.25 / days)
    return ((1 + apr / periods_per_year / 100) ** periods_per_year - 1) * 100



def staking_stats(request):
    with connection.cursor() as cursor:
        query = """
        select count(*) as count, sum(staked_amount) as total_staked from (
            select user_address, sum(
                case
                when is_staked then amount
                else staked_amount * -1
                end
            ) as staked_amount from core_ognstaked group by user_address
        ) as t where staked_amount > 0;
        """
        cursor.execute(query)
        row = cursor.fetchone()
        count, total_staked = row

        data = {
            "success": True,
            "userCount": count,
            "lockupSum": float(total_staked) if total_staked else 0,
        }
        return JsonResponse(data)


def staking_stats_by_duration(request):
    stats = active_stake_stats()

    return JsonResponse({
        "success": True,
        "data": [
            [row['duration'], float(row['total_staked'])]
            for row in stats
        ],
    })


def coingecko_pools(request):
    """ API for CoinGecko to consume to get details about OUSD and OGN """
    ousd_liquidity = totalSupply(OUSD, 18)
    ousd_apy = _get_trailing_apy()
    ogn_stats = active_stake_stats()
    ogn_30_liquidity = 0
    ogn_90_liquidity = 0
    ogn_365_liquidity = 0

    for stat in ogn_stats:
        if stat['duration'] == 30:
            ogn_30_liquidity = stat['total_staked']
        elif stat['duration'] == 90:
            ogn_90_liquidity = stat['total_staked']
        elif stat['duration'] == 365:
            ogn_365_liquidity = stat['total_staked']

    ousd_price = get_price("OUSD").get('usd', 0)
    ogn_price = get_price("OGN").get('usd', 0)

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
                }
            ],
            safe=False
        )
    )
