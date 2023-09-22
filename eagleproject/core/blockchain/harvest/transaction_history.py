from decimal import *
from django import db
from operator import attrgetter
from multiprocessing import (
    Process,
    Manager,
)

from core.models import (
    Log,
    TokenTransfer,
    Block,
    Transaction,
    AnalyticsReport,
    Subscriber,
    OriginTokens
)

from core.blockchain.strategies import (
    OETH_VAULT,
    OUSD_VAULT,
)

from core.blockchain.sigs import (
    TRANSFER,
    SIG_EVENT_YIELD_DISTRIBUTION
)

from django.db.models import Q
from core.blockchain.harvest.transactions import (
    explode_log_data
)
from core.blockchain.harvest.snapshots import (
    build_asset_block,
    latest_snapshot_block_number
)
from core.blockchain.rpc import (
    creditsBalanceOf,
    balanceOf,
    totalSupply,
    dripper_available,
    OUSDMetaStrategy,
    OETHCurveAMOStrategy
)
from core.blockchain.apy import (
    get_trailing_apy,
    to_apy
)
from datetime import ( datetime, timedelta, timezone )

from core.blockchain.const import (
    START_OF_EVERYTHING_TIME,
    report_stats,
    curve_report_stats,
    oeth_report_stats,
    E_18,
    START_OF_CURVE_CAMPAIGN_TIME,
    START_OF_OUSD_V2,
    START_OF_OETH,
    BLOCKS_PER_DAY,
    OUSD_TOTAL_SUPPLY_UPDATED_TOPIC,
    OUSD_TOTAL_SUPPLY_UPDATED_HIGHRES_TOPIC,
    VAULT_FEE_UPGRADE_BLOCK
)

from typing import List

from core.blockchain.utils import (
    chunks,
)
from core.blockchain.harvest.snapshots import (
    ensure_asset,
    ensure_supply_snapshot,
    calculate_ousd_snapshot_data,
    calculate_oeth_snapshot_data,
)

from core.blockchain.harvest.blocks import ensure_block, ensure_day

import calendar

from core.channels.email import (
    Email
)
from django.template.loader import render_to_string
from django.conf import settings
from core.blockchain.decode import slot
from core.blockchain.addresses import (
    CONTRACT_ADDR_TO_NAME,
    CURVE_METAPOOL,
    CURVE_METAPOOL_GAUGE,
    OGV,
    VEOGV,
    OUSD,
    OETH,
    WOUSD,
    WOETH,
    OETH_ETH_AMO_METAPOOL,
    OETH_ETH_AMO_CURVE_GUAGE,
)

from core.coingecko import get_coin_history
from core.defillama import get_stablecoin_market_cap

import simplejson as json

from django.core.exceptions import ObjectDoesNotExist

from eth_abi import decode_single
from eth_utils import decode_hex

ACCOUNT_ANALYZE_PARALLELISM=30

class rebase_log:
    # block_number
    # credits_per_token
    # balance

    def __init__(self, block_number, position, credits_per_token, tx_hash):
        self.block_number = block_number
        self.position = position
        self.credits_per_token = credits_per_token
        self.tx_hash = tx_hash

    def set_block_time(self, block_time):
        self.block_time = block_time

    def __str__(self):
        return 'rebase log: block: {} creditsPerToken: {} balance: {} block_time:{}'.format(self.block_number, self.credits_per_token, self.balance if hasattr(self, 'balance') else 0, self.block_time if hasattr(self, 'block_time') else False)

class transfer_log:
    # block_number
    # amount
    # credits_per_token
    # balance

    def __init__(self, block_number, position, tx_hash, amount, from_address, to_address, block_time, log_index):
        self.block_number = block_number
        self.position = position
        self.tx_hash = tx_hash
        self.amount = amount
        self.from_address = from_address
        self.to_address = to_address
        self.block_time = block_time
        self.log_index = log_index

    def __str__(self):
        return 'transfer log: block: {} amount: {} tx_hash: {} creditsPerToken: {} balance: {}'.format(self.block_number, self.amount, self.tx_hash, self.credits_per_token if hasattr(self, 'credits_per_token') else 'N/A', self.balance if hasattr(self, 'balance') else 'N/A')

class address_analytics:
    # OUSD increasing/decreasing is ignoring rebase events
    def __init__(self, is_holding_ousd, is_holding_more_than_100_ousd, is_new_account, has_ousd_increased, has_ousd_decreased, is_new_after_curve_start, new_after_curve_and_hold_more_than_100):
        self.is_holding_ousd = is_holding_ousd
        self.is_holding_more_than_100_ousd = is_holding_more_than_100_ousd
        self.is_new_account = is_new_account
        self.has_ousd_increased = has_ousd_increased
        self.has_ousd_decreased = has_ousd_decreased
        self.is_new_after_curve_start = is_new_after_curve_start
        self.new_after_curve_and_hold_more_than_100 = new_after_curve_and_hold_more_than_100

    def __str__(self):
        return 'address_analytics: is_holding_ousd: {self.is_holding_ousd} is_holding_more_than_100_ousd: {self.is_holding_more_than_100_ousd} is_new_account: {self.is_new_account} has_ousd_increased: {self.has_ousd_increased} has_ousd_decreased: {self.has_ousd_decreased} is_new_after_curve_start: {self.is_new_after_curve_start} new_after_curve_and_hold_more_than_100: {self.new_after_curve_and_hold_more_than_100}'.format(self=self)

class oeth_address_analytics:
    # OETH increasing/decreasing is ignoring rebase events
    def __init__(self, is_holding_oeth, is_holding_more_than_dot1_oeth, is_new_account, has_oeth_increased, has_oeth_decreased):
        self.is_holding_oeth = is_holding_oeth
        self.is_holding_more_than_dot1_oeth = is_holding_more_than_dot1_oeth
        self.is_new_account = is_new_account
        self.has_oeth_increased = has_oeth_increased
        self.has_oeth_decreased = has_oeth_decreased

    def __str__(self):
        return 'oeth_address_analytics: is_holding_oeth: {self.is_holding_oeth} is_holding_more_than_dot1_oeth: {self.is_holding_more_than_dot1_oeth} is_new_account: {self.is_new_account} has_oeth_increased: {self.has_oeth_increased} has_oeth_decreased: {self.has_oeth_decreased}'.format(self=self)


class analytics_report:
    def __init__(
        self,

        # OUSD
        accounts_analyzed,
        accounts_holding_ousd,
        accounts_holding_more_than_100_ousd,
        accounts_holding_more_than_100_ousd_after_curve_start,
        new_accounts,
        new_accounts_after_curve_start,
        accounts_with_non_rebase_balance_increase,
        accounts_with_non_rebase_balance_decrease,
        supply_data,
        apy,
        apy_7d,
        curve_data,
        fees_generated,
        fees_distributed,
        average_ousd_volume,
        stablecoin_market_share,

        # OGV
        ogv_data,

        # OETH data
        oeth_accounts_analyzed,
        accounts_holding_oeth,
        accounts_holding_more_than_dot1_oeth,
        oeth_new_accounts,
        oeth_accounts_with_non_rebase_balance_increase,
        oeth_accounts_with_non_rebase_balance_decrease,
        oeth_supply_data,
        oeth_apy,
        oeth_apy_7d,
        oeth_curve_data,
        oeth_fees_generated,
        oeth_fees_distributed,
        average_oeth_volume,
        average_oeth_price,
    ):
        self.accounts_analyzed = accounts_analyzed
        self.accounts_holding_ousd = accounts_holding_ousd
        self.accounts_holding_more_than_100_ousd = accounts_holding_more_than_100_ousd
        self.accounts_holding_more_than_100_ousd_after_curve_start = accounts_holding_more_than_100_ousd_after_curve_start
        self.new_accounts = new_accounts
        self.new_accounts_after_curve_start = new_accounts_after_curve_start
        self.accounts_with_non_rebase_balance_increase = accounts_with_non_rebase_balance_increase
        self.accounts_with_non_rebase_balance_decrease = accounts_with_non_rebase_balance_decrease
        self.supply_data = supply_data
        self.apy = apy
        self.apy_7d = apy_7d
        self.curve_data = curve_data
        self.fees_generated = fees_generated
        self.fees_distributed = fees_distributed
        self.average_ousd_volume = average_ousd_volume
        self.stablecoin_market_share = stablecoin_market_share
        self.ogv_data = ogv_data

        self.oeth_accounts_analyzed = oeth_accounts_analyzed
        self.accounts_holding_oeth = accounts_holding_oeth
        self.accounts_holding_more_than_dot1_oeth = accounts_holding_more_than_dot1_oeth
        self.oeth_new_accounts = oeth_new_accounts
        self.oeth_accounts_with_non_rebase_balance_increase = oeth_accounts_with_non_rebase_balance_increase
        self.oeth_accounts_with_non_rebase_balance_decrease = oeth_accounts_with_non_rebase_balance_decrease
        self.oeth_supply_data = oeth_supply_data
        self.oeth_apy = oeth_apy
        self.oeth_apy_7d = oeth_apy_7d
        self.oeth_curve_data = oeth_curve_data
        self.oeth_fees_generated = oeth_fees_generated
        self.oeth_fees_distributed = oeth_fees_distributed
        self.average_oeth_volume = average_oeth_volume
        self.average_oeth_price = average_oeth_price

    def __str__(self):
        return 'Analytics report: accounts_analyzed: {} accounts_holding_ousd: {} accounts_holding_more_than_100_ousd: {} accounts_holding_more_than_100_ousd_after_curve_start: {} new_accounts: {} new_accounts_after_curve_start: {} accounts_with_non_rebase_balance_increase: {} accounts_with_non_rebase_balance_decrease: {} apy: {} supply_data: {} curve_data: {} fees_generated: {} average_ousd_volume: {} stablecoin_market_share: {} ogv_data: {}'.format(self.accounts_analyzed, self.accounts_holding_ousd, self.accounts_holding_more_than_100_ousd, self.accounts_holding_more_than_100_ousd_after_curve_start, self.new_accounts, self.new_accounts_after_curve_start, self.accounts_with_non_rebase_balance_increase, self.accounts_with_non_rebase_balance_decrease, self.apy, self.supply_data, self.curve_data, self.fees_generated, self.average_ousd_volume, self.stablecoin_market_share, self.ogv_data)

class transaction_analysis:
    def __init__(
        self,
        account,
        tx_hash,
        contract_address,
        internal_transactions,
        received_eth,
        sent_eth,
        transfer_origin_token_out, # origin_token == OETH/OUSD
        transfer_origin_token_in,
        transfer_coin_out,
        transfer_coin_in,
        origin_token_transfer_from,
        origin_token_transfer_to,
        origin_token_transfer_amount,
        transfer_log_count,
        classification,
        project=OriginTokens.OUSD
    ):
        self.account = account
        self.tx_hash = tx_hash
        self.contract_address = contract_address
        self.internal_transactions = internal_transactions
        self.received_eth = received_eth
        self.sent_eth = sent_eth
        self.transfer_origin_token_out = transfer_origin_token_out
        self.transfer_origin_token_in = transfer_origin_token_in
        self.transfer_coin_out = transfer_coin_out
        self.transfer_coin_in = transfer_coin_in
        self.origin_token_transfer_from = origin_token_transfer_from
        self.origin_token_transfer_to = origin_token_transfer_to
        self.origin_token_transfer_amount = origin_token_transfer_amount
        self.transfer_log_count = transfer_log_count
        self.classification = classification
        self.project = project

    def __str__(self):
        return 'transaction analysis: account: {} tx_hash: {} classification: {} contract_address: {} received_eth: {} sent_eth: {} transfer_origin_token_out: {} transfer_origin_token_in: {} transfer_coin_out {} transfer_coin_in {} origin_token_transfer_from {} origin_token_transfer_to {} origin_token_transfer_amount {} transfer_log_count {}'.format(
            self.account,
            self.tx_hash,
            self.classification,
            self.contract_address,
            self.received_eth,
            self.sent_eth,
            self.transfer_origin_token_out,
            self.transfer_origin_token_in,
            self.transfer_coin_out,
            self.transfer_coin_in,
            self.origin_token_transfer_from,
            self.origin_token_transfer_to,
            self.origin_token_transfer_amount,
            self.transfer_log_count
        )


# get first available block from the given time.
# Ascending=True -> closest youngest block
# Ascending=False -> closest oldest block
def get_block_number_from_block_time(time, ascending = False):
    if ascending :
        result = Block.objects.filter(block_time__gte=time).order_by('block_time')[:1]
    else:
        result = Block.objects.filter(block_time__lte=time).order_by('-block_time')[:1]

    if len(result) != 1:
        raise Exception('Can not find block time {} than {}'.format('younger' if ascending else 'older', str(time)))
    return result[0].block_number

def calculate_report_change(current_report, previous_report):
    changes = {
        "circulating_ousd": 0,
        "protocol_owned_ousd": 0,
        "apy": 0,
        "apy_7d": 0,
        "accounts_analyzed": 0,
        "accounts_holding_ousd": 0,
        "accounts_holding_more_than_100_ousd": 0,
        "accounts_holding_more_than_100_ousd_after_curve_start": 0,
        "new_accounts": 0,
        "new_accounts_after_curve_start": 0,
        "accounts_with_non_rebase_balance_increase": 0,
        "accounts_with_non_rebase_balance_decrease": 0,
        "other_rebasing": 0,
        "other_non_rebasing": 0,
        "curve_metapool_total_supply": 0,
        "share_earning_curve_ogn": 0,
        "fees_generated": 0,
        "fees_distributed": 0,
        "curve_supply": 0,
        "average_ousd_volume": 0,
        "stablecoin_market_share": 0,
        
        # OGV
        "ogv_price": 0,
        "ogv_market_cap": 0,
        "average_ogv_volume": 0,
        "amount_staked": 0,
        "percentage_staked": 0,

        # OETH
        "circulating_oeth": 0,
        "protocol_owned_oeth": 0,
        "oeth_apy": 0,
        "oeth_apy_7d": 0,
        "oeth_accounts_analyzed": 0,
        "accounts_holding_oeth": 0,
        "accounts_holding_more_than_dot1_oeth": 0,
        "oeth_new_accounts": 0,
        "oeth_accounts_with_non_rebase_balance_increase": 0,
        "oeth_accounts_with_non_rebase_balance_decrease": 0,
        "oeth_other_rebasing": 0,
        "oeth_other_non_rebasing": 0,
        "oeth_curve_metapool_total_supply": 0,
        "oeth_fees_generated": 0,
        "oeth_fees_distributed": 0,
        "oeth_curve_supply": 0,
        "average_oeth_volume": 0,
    }

    def calculate_difference(current_stat, previous_stat):
        if current_stat == 0 or current_stat is None or previous_stat == 0 or previous_stat is None:
            return 0

        return (current_stat - previous_stat) / previous_stat * 100

    def calculate_difference_bp(current_stat, previous_stat):
        if current_stat == 0 or current_stat is None or previous_stat == 0 or previous_stat is None:
            return 0

        return (current_stat - previous_stat) * 100

    if previous_report is None:
        return changes

    json_report = json.loads(str(current_report.report))
    json_report_previous = json.loads(str(previous_report.report))

    supply_data = json_report["supply_data"] if "supply_data" in json_report else None
    supply_data_previous = json_report_previous["supply_data"] if "supply_data" in json_report_previous else None

    oeth_supply_data = json_report["oeth_supply_data"] if "oeth_supply_data" in json_report else None
    oeth_supply_data_previous = json_report_previous["oeth_supply_data"] if "oeth_supply_data" in json_report_previous else None

    ogv_data = json_report["ogv_data"] if "ogv_data" in json_report else None
    ogv_data_previous = json_report_previous["ogv_data"] if "ogv_data" in json_report_previous else None

    curve_data = json_report["curve_data"] if "curve_data" in json_report else None
    curve_data_previous = json_report_previous["curve_data"] if "curve_data" in json_report_previous else None

    oeth_curve_data = json_report["oeth_curve_data"] if "oeth_curve_data" in json_report else None
    oeth_curve_data_previous = json_report_previous["oeth_curve_data"] if "oeth_curve_data" in json_report_previous else None

    # OUSD
    changes['circulating_ousd'] = calculate_difference(current_report.circulating_ousd, previous_report.circulating_ousd)
    changes['protocol_owned_ousd'] = calculate_difference(current_report.protocol_owned_ousd, previous_report.protocol_owned_ousd)
    changes['apy'] = calculate_difference_bp(current_report.apy, previous_report.apy)
    changes['apy_7d'] = calculate_difference_bp(current_report.apy_7d, previous_report.apy_7d)
    changes['accounts_analyzed'] = calculate_difference(current_report.accounts_analyzed, previous_report.accounts_analyzed)
    changes['accounts_holding_ousd'] = calculate_difference(current_report.accounts_holding_ousd, previous_report.accounts_holding_ousd)
    changes['accounts_holding_more_than_100_ousd'] = calculate_difference(current_report.accounts_holding_more_than_100_ousd, previous_report.accounts_holding_more_than_100_ousd)
    changes['accounts_holding_more_than_100_ousd_after_curve_start'] = calculate_difference(current_report.accounts_holding_more_than_100_ousd_after_curve_start, previous_report.accounts_holding_more_than_100_ousd_after_curve_start)
    changes['new_accounts'] = calculate_difference(current_report.new_accounts, previous_report.new_accounts)
    changes['new_accounts_after_curve_start'] = calculate_difference(current_report.new_accounts_after_curve_start, previous_report.new_accounts_after_curve_start)
    changes['accounts_with_non_rebase_balance_increase'] = calculate_difference(current_report.accounts_with_non_rebase_balance_increase, previous_report.accounts_with_non_rebase_balance_increase)
    changes['accounts_with_non_rebase_balance_decrease'] = calculate_difference(current_report.accounts_with_non_rebase_balance_decrease, previous_report.accounts_with_non_rebase_balance_decrease)
    changes['fees_generated'] = calculate_difference(current_report.fees_generated, previous_report.fees_generated)
    changes['fees_distributed'] = calculate_difference(current_report.fees_distributed, previous_report.fees_distributed)
    changes['curve_supply'] = calculate_difference(current_report.curve_supply, previous_report.curve_supply)
    changes['average_ousd_volume'] = calculate_difference(current_report.average_ousd_volume, previous_report.average_ousd_volume)
    changes['stablecoin_market_share'] = calculate_difference_bp(current_report.stablecoin_market_share, previous_report.stablecoin_market_share)

    # OETH
    changes['circulating_oeth'] = calculate_difference(current_report.circulating_oeth, previous_report.circulating_oeth)
    changes['protocol_owned_oeth'] = calculate_difference(current_report.protocol_owned_oeth, previous_report.protocol_owned_oeth)
    changes['oeth_apy'] = calculate_difference_bp(current_report.oeth_apy, previous_report.oeth_apy)
    changes['oeth_apy_7d'] = calculate_difference_bp(current_report.oeth_apy_7d, previous_report.oeth_apy_7d)
    changes['oeth_accounts_analyzed'] = calculate_difference(current_report.oeth_accounts_analyzed, previous_report.oeth_accounts_analyzed)
    changes['accounts_holding_oeth'] = calculate_difference(current_report.accounts_holding_oeth, previous_report.accounts_holding_oeth)
    changes['accounts_holding_more_than_dot1_oeth'] = calculate_difference(current_report.accounts_holding_more_than_dot1_oeth, previous_report.accounts_holding_more_than_dot1_oeth)
    changes['oeth_new_accounts'] = calculate_difference(current_report.oeth_new_accounts, previous_report.oeth_new_accounts)
    changes['oeth_accounts_with_non_rebase_balance_increase'] = calculate_difference(current_report.oeth_accounts_with_non_rebase_balance_increase, previous_report.oeth_accounts_with_non_rebase_balance_increase)
    changes['oeth_accounts_with_non_rebase_balance_decrease'] = calculate_difference(current_report.oeth_accounts_with_non_rebase_balance_decrease, previous_report.oeth_accounts_with_non_rebase_balance_decrease)
    changes['oeth_fees_generated'] = calculate_difference(current_report.oeth_fees_generated, previous_report.oeth_fees_generated)
    changes['oeth_fees_distributed'] = calculate_difference(current_report.oeth_fees_distributed, previous_report.oeth_fees_distributed)
    changes['oeth_curve_supply'] = calculate_difference(current_report.oeth_curve_supply, previous_report.oeth_curve_supply)
    changes['average_oeth_volume'] = calculate_difference(current_report.average_oeth_volume, previous_report.average_oeth_volume)

    # OGV
    changes['ogv_price'] = calculate_difference(current_report.ogv_price, previous_report.ogv_price)
    changes['ogv_market_cap'] = calculate_difference(current_report.ogv_market_cap, previous_report.ogv_market_cap)
    changes['average_ogv_volume'] = calculate_difference(current_report.average_ogv_volume, previous_report.average_ogv_volume)
    changes['amount_staked'] = calculate_difference(current_report.amount_staked, previous_report.amount_staked)
    changes['percentage_staked'] = calculate_difference_bp(current_report.percentage_staked, previous_report.percentage_staked)

    if supply_data is not None and supply_data_previous is not None:
        changes['other_rebasing'] = calculate_difference(supply_data['other_rebasing'], supply_data_previous['other_rebasing'])
        changes['other_non_rebasing'] = calculate_difference(supply_data['other_non_rebasing'], supply_data_previous['other_non_rebasing'])
    if oeth_supply_data is not None and oeth_supply_data_previous is not None:
        changes['oeth_other_rebasing'] = calculate_difference(oeth_supply_data['other_rebasing'], oeth_supply_data_previous.get('other_rebasing', 0))
        changes['oeth_other_non_rebasing'] = calculate_difference(oeth_supply_data['other_non_rebasing'], oeth_supply_data_previous.get('other_non_rebasing', 0))

    if curve_data is not None and curve_data_previous is not None:
        changes['curve_metapool_total_supply'] = calculate_difference(current_report.curve_metapool_total_supply, previous_report.curve_metapool_total_supply)
        changes['share_earning_curve_ogn'] = calculate_difference(current_report.share_earning_curve_ogn, previous_report.share_earning_curve_ogn)

    if oeth_curve_data is not None and oeth_curve_data_previous is not None:
        changes['oeth_curve_metapool_total_supply'] = calculate_difference(current_report.oeth_curve_metapool_total_supply, previous_report.oeth_curve_metapool_total_supply)

    return changes

def upsert_report(
    week_option, 
    month_option, 
    year, 
    status, 
    report, 
    block_start_number, 
    block_end_number, 
    start_time, 
    end_time, 
    do_only_transaction_analytics, 
    transaction_report, 
    oeth_transaction_report
):
    analyticsReport = None

    params = {
        "block_start": block_start_number,
        "block_end": block_end_number,
        "start_time": start_time,
        "end_time": end_time,
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
        "status": status,
        # OUSD
        "accounts_analyzed": report.accounts_analyzed if report is not None else 0,
        "accounts_holding_ousd": report.accounts_holding_ousd if report is not None else 0,
        "accounts_holding_more_than_100_ousd": report.accounts_holding_more_than_100_ousd if report is not None else 0,
        "accounts_holding_more_than_100_ousd_after_curve_start": report.accounts_holding_more_than_100_ousd_after_curve_start if report is not None else 0,
        "new_accounts": report.new_accounts if report is not None else 0,
        "new_accounts_after_curve_start": report.new_accounts_after_curve_start if report is not None else 0,
        "accounts_with_non_rebase_balance_increase": report.accounts_with_non_rebase_balance_increase if report is not None else 0,
        "accounts_with_non_rebase_balance_decrease": report.accounts_with_non_rebase_balance_decrease if report is not None else 0,
        "transaction_report": transaction_report,
        "report": json.dumps(report.__dict__) if report is not None else '[]',
        # OETH
        "oeth_accounts_analyzed": report.oeth_accounts_analyzed if report is not None else 0,
        "accounts_holding_oeth": report.accounts_holding_oeth if report is not None else 0,
        "accounts_holding_more_than_dot1_oeth": report.accounts_holding_more_than_dot1_oeth if report is not None else 0,
        "oeth_new_accounts": report.oeth_new_accounts if report is not None else 0,
        "oeth_accounts_with_non_rebase_balance_increase": report.accounts_with_non_rebase_balance_increase if report is not None else 0,
        "oeth_accounts_with_non_rebase_balance_decrease": report.accounts_with_non_rebase_balance_decrease if report is not None else 0,
        "oeth_transaction_report": oeth_transaction_report,
    }

    if do_only_transaction_analytics:
        if week_option != None:
            analyticsReport = AnalyticsReport.objects.get(
                week=week_option,
                year=year,
            )
        else:
            analyticsReport = AnalyticsReport.objects.get(
                month=month_option,
                year=year,
            )

        if analyticsReport is None:
            raise Exception('Report not found week: {} month: {} year: {}'.format(week_option, month_option, year))

        analyticsReport.transaction_report = transaction_report
        analyticsReport.save()
    else:
        if week_option != None:
            analyticsReport, created = AnalyticsReport.objects.get_or_create(
                week=week_option,
                year=year,
                defaults=params,
            )
        else:
            analyticsReport, created = AnalyticsReport.objects.get_or_create(
                month=month_option,
                year=year,
                defaults=params,
            )

        if not created:
            for key in params.keys():
                if key == 'created_at':
                    continue

                setattr(analyticsReport, key, params.get(key))
            analyticsReport.save()

    return analyticsReport

def create_time_interval_report_for_previous_week(year_override, week_override, do_only_transaction_analytics = False):
    year_number = year_override if year_override is not None else datetime.now().year
    # number of the week in a year - for the previous week
    week_number = week_override if week_override is not None else int(datetime.now().strftime("%W")) - 1

    if week_override is not None and week_override > int(datetime.now().strftime("%W")) - 1 and year_override is not None and year_override >= datetime.now().year:
        print("Week {} of year {} has not ended yet.".format(week_number, year_number))
        return

    if week_override is None and not should_create_new_report(year_number, None, week_number):
        print("Report for year: {} and week: {} does not need creation".format(year_number, week_number))
        return

    # TODO: this will work incorrectly when the week falls on new year
    week_interval = "{year}-W{week}".format(year = year_number, week=week_number)

    # Monday of selected week
    start_time = datetime.strptime(week_interval + '-1', "%Y-W%W-%w")
    # Sunday of selected week
    end_time = datetime.strptime(week_interval + '-0', "%Y-W%W-%w").replace(hour=23, minute=59, second=59)

    block_start_number = get_block_number_from_block_time(start_time, True)
    block_end_number = get_block_number_from_block_time(end_time, False)

    transaction_report = do_transaction_analytics(block_start_number, block_end_number, start_time, end_time, project=OriginTokens.OUSD)
    oeth_transaction_report = do_transaction_analytics(block_start_number, block_end_number, start_time, end_time, project=OriginTokens.OETH)

    upsert_report(
        week_number,
        None,
        year_number,
        "processing",
        None,
        block_start_number,
        block_end_number,
        start_time,
        end_time,
        do_only_transaction_analytics,
        transaction_report,
        oeth_transaction_report
    )

    # don't do the general report if not needed
    if do_only_transaction_analytics:
        return

    report = create_time_interval_report(
        block_start_number,
        block_end_number,
        start_time,
        end_time,
    )

    db_report = upsert_report(
        week_number,
        None,
        year_number,
        "done",
        report,
        block_start_number,
        block_end_number,
        start_time,
        end_time,
        do_only_transaction_analytics,
        transaction_report,
        oeth_transaction_report
    )

    # if it is a cron job report
    if week_override is None:
        # if first week of the year report
        if (week_number == 0):
            week_number = 53
            year_number -= 1
        else :
            week_number -= 1

        week_before_report = AnalyticsReport.objects.filter(Q(year=year_number) & Q(week=week_number))
        preb_db_report = week_before_report[0] if len(week_before_report) != 0 else None
        send_report_email('Origin DeFi Analytics Weekly Report', db_report, preb_db_report, "Weekly")

def should_create_new_report(year, month_option, week_option):
    try:
        if month_option is not None:
            existing_report = AnalyticsReport.objects.filter(Q(year=year) & Q(month=month_option)).first()
        elif week_option is not None:
            existing_report = AnalyticsReport.objects.filter(Q(year=year) & Q(week=week_option)).first()
        if existing_report is None:
            return True
    except ObjectDoesNotExist:
        return True
    

    # nothing to do here, report is already done
    if existing_report.status == 'done':
        return False

    # in seconds
    report_age = (datetime.now() - existing_report.updated_at.replace(tzinfo=None)).total_seconds()

    # report might still be processing
    if report_age < 3 * 60 * 60:
        return False

    return True

def create_time_interval_report_for_previous_month(year_override, month_override, do_only_transaction_analytics = False):
    # number of the month in a year - for the previous month
    month_number = month_override if month_override is not None else int(datetime.now().strftime("%m")) - 1
    year_number = year_override if year_override is not None else datetime.now().year + (-1 if month_number == 12 else 0)

    if month_override is not None and month_override > int(datetime.now().strftime("%m")) - 1 and year_override is not None and year_override >= datetime.now().year:
        print("Month {} of year {} has not ended yet.".format(month_number, year_number))
        return

    if month_override is None and not should_create_new_report(year_number, month_number, None):
        print("Report for year: {} and month: {} does not need creation".format(year_number, month_number))
        return

    month_interval = "{year}-m{month}".format(year=year_number, month=month_number)

    (start_day, end_day) = calendar.monthrange(year_number, month_number)

    # Monday of selected week
    start_time = datetime.strptime(month_interval + '-1', "%Y-m%m-%d")
    # Sunday of selected week
    end_time = datetime.strptime(month_interval + '-{}'.format(end_day), "%Y-m%m-%d").replace(hour=23, minute=59, second=59)

    block_start_number = get_block_number_from_block_time(start_time, True)
    block_end_number = get_block_number_from_block_time(end_time, False)

    transaction_report = do_transaction_analytics(block_start_number, block_end_number, start_time, end_time, project=OriginTokens.OUSD)
    oeth_transaction_report = do_transaction_analytics(block_start_number, block_end_number, start_time, end_time, project=OriginTokens.OETH)

    upsert_report(
        None,
        month_number,
        year_number,
        "processing",
        None,
        block_start_number,
        block_end_number,
        start_time,
        end_time,
        do_only_transaction_analytics,
        transaction_report,
        oeth_transaction_report
    )

    # don't do the general report if not needed
    if do_only_transaction_analytics:
        return

    report = create_time_interval_report(
        block_start_number,
        block_end_number,
        start_time,
        end_time,
    )

    db_report = upsert_report(
        None,
        month_number,
        year_number,
        "done",
        report,
        block_start_number,
        block_end_number,
        start_time,
        end_time,
        do_only_transaction_analytics,
        transaction_report,
        oeth_transaction_report
    )

    # if it is a cron job report
    if month_override is None:
        # if first month of the year report
        if (month_number == 1):
            month_number = 12
            year_number -= 1
        else :
            month_number -= 1

        month_before_report = AnalyticsReport.objects.filter(Q(year=year_number) & Q(month=month_number))
        preb_db_report = month_before_report[0] if len(month_before_report) != 0 else None
        send_report_email('Origin DeFi Analytics Monthly Report', db_report, preb_db_report, "Monthly")


def backfill_subscribers():
    emails = settings.REPORT_RECEIVER_EMAIL_LIST.split(",")
    for email in emails:
        if Subscriber.objects.filter(email=email).first() is None:
            sub = Subscriber(email=email, conf_num=generate_token(), confirmed=True)
            sub.save()


def get_block_time_from_block_number(number):
    result = Block.objects.filter(block_number__gte=number).order_by('block_time')[:1]

    if len(result) != 1:
        raise Exception('Can not find block time for block number', START_OF_PROJECT)

    return result[0].block_time


def backfill_daily_stats(project=OriginTokens.OUSD):
    START_OF_PROJECT = START_OF_OUSD_V2 if project == OriginTokens.OUSD else START_OF_OETH
    start_time = get_block_time_from_block_number(START_OF_PROJECT)
    latest_time = get_block_time_from_block_number(latest_snapshot_block_number(project))
    days = (latest_time - start_time).days
    _daily_rows(int(days), latest_snapshot_block_number(project), project=project)
    return


# get all accounts that at some point held OUSD
def fetch_all_holders(project=OriginTokens.OUSD):
    to_addresses = list(map(lambda log: log['to_address'], TokenTransfer.objects.filter(project=project).values('to_address').distinct()))
    from_addresses = list(map(lambda log: log['from_address'], TokenTransfer.objects.filter(project=project).values('from_address').distinct()))
    return list(set(filter(lambda address: address not in ['0x0000000000000000000000000000000000000000', '0x000000000000000000000000000000000000dead'], to_addresses + from_addresses)))


def fetch_supply_data(block_number, project=OriginTokens.OUSD):
    ensure_supply_snapshot(block_number, project=project)
    
    if project == OriginTokens.OUSD:
        [pools, totals_by_rebasing, other_rebasing, other_non_rebasing, snapshot] = calculate_ousd_snapshot_data(block_number)
        
        ousd = build_asset_block("OUSD", block_number, project=project)
        protocol_owned_ousd = float(ousd.strat_holdings["ousd_metastrat"])
        circulating_ousd = float(snapshot.reported_supply) - protocol_owned_ousd

        return {
            'circulating_ousd': circulating_ousd,
            'protocol_owned_ousd': protocol_owned_ousd,
            'pools': pools,
            'totals_by_rebasing': totals_by_rebasing,
            'other_rebasing': other_rebasing,
            'other_non_rebasing': other_non_rebasing,
        }
    else:
        [pools, totals_by_rebasing, other_rebasing, other_non_rebasing, snapshot] = calculate_oeth_snapshot_data(block_number)

        oeth = build_asset_block("OETH", block_number, project=project)
        protocol_owned_oeth = float(oeth.strat_holdings["oeth_curve_amo"])
        circulating_oeth = float(snapshot.reported_supply) - protocol_owned_oeth

        return {
            'circulating_oeth': circulating_oeth,
            'protocol_owned_oeth': protocol_owned_oeth,
            'pools': pools,
            'totals_by_rebasing': totals_by_rebasing,
            'other_rebasing': other_rebasing,
            'other_non_rebasing': other_non_rebasing,
        }

def fetch_ogv_data(to_block, from_timestamp, to_timestamp):
    try:
        ogv_history = get_coin_history('OGV', from_timestamp, to_timestamp)
        index = len(ogv_history['prices']) - 1

        price = ogv_history['prices'][index][1]
        market_cap = ogv_history['market_caps'][index][1]
        volume = ogv_history['total_volumes'][index][1]

        amount_staked = balanceOf(OGV, VEOGV, 18, to_block)
        total_supply = totalSupply(OGV, 18, to_block)
        percentage_staked = (amount_staked / total_supply) * 100
    except:
        raise Exception(
            "Failed to fetch OGV data"
        )

    return {
        'price': price,
        'market_cap': market_cap,
        'volume': volume,
        'amount_staked': amount_staked,
        'percentage_staked': percentage_staked,
    }

def get_curve_data(to_block, project=OriginTokens.OUSD):
    if project == OriginTokens.OUSD:
        balance = balanceOf(CURVE_METAPOOL, CURVE_METAPOOL_GAUGE, 18, to_block)
        supply = totalSupply(CURVE_METAPOOL, 18, to_block)
        return {
            "total_supply": supply,
            "earning_ogn": balance/supply,
        }
    else:
        supply = totalSupply(OETH_ETH_AMO_METAPOOL, 18, to_block)
        return {
            "total_supply": supply
        }

def create_time_interval_report(from_block, to_block, from_block_time, to_block_time):
    decimal_context = getcontext()
    decimal_prec = decimal_context.prec
    decimal_rounding = decimal_context.rounding

    # to simulate uint256 in solidity when using decimals
    decimal_context.prec = 18
    decimal_context.rounding = 'ROUND_DOWN'

    all_ousd_addresses = fetch_all_holders(project=OriginTokens.OUSD)
    all_oeth_addresses = fetch_all_holders(project=OriginTokens.OETH)

    ousd_rebase_logs = get_rebase_logs(from_block, to_block, project=OriginTokens.OUSD)
    oeth_rebase_logs = get_rebase_logs(from_block, to_block, project=OriginTokens.OETH)
    ousd_analysis_list = []
    oeth_analysis_list = []

    from_timestamp = int(from_block_time.strftime('%s'))
    to_timestamp = int(to_block_time.strftime('%s'))

    ousd_supply_data = fetch_supply_data(to_block, project=OriginTokens.OUSD)
    ousd_apy = get_trailing_apy(to_block, project=OriginTokens.OUSD)
    ousd_apy_7d = get_trailing_apy(to_block, days=7, project=OriginTokens.OUSD)
    curve_data = get_curve_data(to_block, project=OriginTokens.OUSD)

    oeth_supply_data = fetch_supply_data(to_block, project=OriginTokens.OETH)
    oeth_apy = get_trailing_apy(to_block, project=OriginTokens.OETH)
    oeth_apy_7d = get_trailing_apy(to_block, days=7, project=OriginTokens.OETH)
    oeth_curve_data = get_curve_data(to_block, project=OriginTokens.OETH)

    ogv_data = fetch_ogv_data(to_block, from_timestamp, to_timestamp)

    # Fees
    ousd_fees_generated = 0
    ousd_fees_distributed = 0
    
    oeth_fees_generated = 0
    oeth_fees_distributed = 0
    
    days = (to_block_time - from_block_time).days + 1
    ousd_rows = _daily_rows_past(days, to_block_time, project=OriginTokens.OUSD)
    oeth_rows = _daily_rows_past(days, to_block_time, project=OriginTokens.OETH)
    
    for row in ousd_rows:
        if row.gain >= 0:
            protocol_fee = 0
            if row.block_number > VAULT_FEE_UPGRADE_BLOCK:
                protocol_fee = row.gain / 5 # 20% fee == 20/100 == 1/5
            else:
                protocol_fee = row.gain / 10 # 10% fee == 10/100 == 1/10

            ousd_fees_generated += protocol_fee
            ousd_fees_distributed += (row.gain - protocol_fee)

            
    for row in oeth_rows:
        if row.gain >= 0:
            protocol_fee = row.gain / 5 # 20% fee == 20/100 == 1/5
            oeth_fees_generated += protocol_fee
            oeth_fees_distributed += (row.gain - protocol_fee)

    # Average OUSD Volume
    ousd_volume_sum = 0
    ousd_history = get_coin_history(OriginTokens.OUSD, from_timestamp, to_timestamp)
    ousd_volume_history = ousd_history['total_volumes']
    for x in ousd_volume_history:
        ousd_volume_sum += x[1]
    average_ousd_volume = ousd_volume_sum / len(ousd_volume_history)

    # Average OETH Volume
    oeth_volume_sum = 0
    oeth_price_sum = 0
    oeth_history = get_coin_history(OriginTokens.OETH, from_timestamp, to_timestamp)
    oeth_volume_history = oeth_history['total_volumes']
    oeth_price_history = oeth_history['prices']
    for x in oeth_volume_history:
        oeth_volume_sum += x[1]
    for x in oeth_price_history:
        oeth_price_sum += x[1]
    average_oeth_price = oeth_price_sum / len(oeth_price_history)
    average_oeth_volume = (oeth_volume_sum / average_oeth_price) / len(oeth_volume_history)

    oeth_market_share = 0 # TODO

    # OUSD Market share
    stablecoin_market_cap_history = get_stablecoin_market_cap()

    stablecoin_market_cap = 0
    for x in reversed(stablecoin_market_cap_history):
        if int(x['date']) <= to_timestamp:
            stablecoin_market_cap = x['totalCirculatingUSD']['peggedUSD']
            break

    ousd_market_cap_history = ousd_history['market_caps']
    index = len(ousd_market_cap_history) - 1

    ousd_market_cap = ousd_market_cap_history[index][1]

    ousd_market_cap = 0
    for x in reversed(ousd_market_cap_history):
        if x[0] / 1000 <= to_timestamp:
            ousd_market_cap = x[1]
            break

    ousd_market_share = (ousd_market_cap / stablecoin_market_cap) * 100


    # Uncomment this to enable parallelism
    # manager = Manager()
    # ousd_analysis_list = manager.list()
    # counter = 0

    # all_chunks = chunks(all_ousd_addresses, ACCOUNT_ANALYZE_PARALLELISM)
    # for chunk in all_chunks:
    #     analyze_account_in_parallel(ousd_analysis_list, counter * ACCOUNT_ANALYZE_PARALLELISM, len(all_ousd_addresses), chunk, rebase_logs, from_block, to_block, from_block_time, to_block_time)
    #     counter += 1

    counter = 0
    for account in all_ousd_addresses:
        analyze_account(ousd_analysis_list, account, ousd_rebase_logs, from_block, to_block, from_block_time, to_block_time, project=OriginTokens.OUSD)
        print('Analyzing account {} of {}'.format(counter, len(all_ousd_addresses)))
        counter += 1

    accounts_analyzed = len(ousd_analysis_list)

    counter = 0
    for account in all_oeth_addresses:
        analyze_account(oeth_analysis_list, account, oeth_rebase_logs, from_block, to_block, from_block_time, to_block_time, project=OriginTokens.OETH)
        print('Analyzing account {} of {}'.format(counter, len(all_oeth_addresses)))
        counter += 1

    oeth_accounts_analyzed = len(oeth_analysis_list)

    # OUSD-specific data
    accounts_holding_ousd = 0
    accounts_holding_more_than_100_ousd = 0
    accounts_holding_more_than_100_ousd_after_curve_start = 0
    new_accounts = 0
    new_accounts_after_curve_start = 0
    accounts_with_non_rebase_balance_increase = 0
    accounts_with_non_rebase_balance_decrease = 0

    # OETH-specific data
    accounts_holding_oeth = 0
    accounts_holding_more_than_dot1_oeth = 0
    oeth_new_accounts = 0
    oeth_accounts_with_non_rebase_balance_increase = 0
    oeth_accounts_with_non_rebase_balance_decrease = 0

    for analysis in ousd_analysis_list:
        new_accounts += 1 if analysis.is_new_account else 0
        accounts_holding_ousd += 1 if analysis.is_holding_ousd else 0
        accounts_holding_more_than_100_ousd += 1 if analysis.is_holding_more_than_100_ousd else 0
        accounts_holding_more_than_100_ousd_after_curve_start += 1 if analysis.new_after_curve_and_hold_more_than_100 else 0
        new_accounts_after_curve_start += 1 if analysis.is_new_after_curve_start else 0
        accounts_with_non_rebase_balance_increase += 1 if analysis.has_ousd_increased else 0
        accounts_with_non_rebase_balance_decrease += 1 if analysis.has_ousd_decreased else 0


    for analysis in oeth_analysis_list:
        oeth_new_accounts += 1 if analysis.is_new_account else 0

        accounts_holding_oeth += 1 if analysis.is_holding_oeth else 0
        accounts_holding_more_than_dot1_oeth += 1 if analysis.is_holding_more_than_dot1_oeth else 0
        oeth_accounts_with_non_rebase_balance_increase += 1 if analysis.has_oeth_increased else 0
        oeth_accounts_with_non_rebase_balance_decrease += 1 if analysis.has_oeth_decreased else 0


    report = analytics_report(
        accounts_analyzed,
        accounts_holding_ousd,
        accounts_holding_more_than_100_ousd,
        accounts_holding_more_than_100_ousd_after_curve_start,
        new_accounts,
        new_accounts_after_curve_start,
        accounts_with_non_rebase_balance_increase,
        accounts_with_non_rebase_balance_decrease,
        ousd_supply_data,
        ousd_apy,
        ousd_apy_7d,
        curve_data,
        ousd_fees_generated,
        ousd_fees_distributed,
        average_ousd_volume,
        ousd_market_share,
        ogv_data,
        oeth_accounts_analyzed,
        accounts_holding_oeth,
        accounts_holding_more_than_dot1_oeth,
        oeth_new_accounts,
        oeth_accounts_with_non_rebase_balance_increase,
        oeth_accounts_with_non_rebase_balance_decrease,
        oeth_supply_data,
        oeth_apy,
        oeth_apy_7d,
        oeth_curve_data,
        oeth_fees_generated,
        oeth_fees_distributed,
        average_oeth_volume,
        average_oeth_price
    )

    # set the values back again
    decimal_context.prec = decimal_prec
    decimal_context.rounding = decimal_rounding
    return report


def analyze_account_in_parallel(analysis_list, accounts_already_analyzed, total_accounts, accounts, rebase_logs, from_block, to_block, from_block_time, to_block_time):
    print("Analyzing {} accounts... progress {}/{}".format(len(accounts), accounts_already_analyzed + len(accounts), total_accounts))
    # Multiprocessing copies connection objects between processes because it forks processes
    # and therefore copies all the file descriptors of the parent process. That being said,
    # a connection to the SQL server is just a file, you can see it in linux under /proc//fd/....
    # any open file will be shared between forked processes.
    # closing all connections just forces the processes to open new connections within the new
    # process.
    # Not doing this causes PSQL connection errors because multiple processes are using a single connection in
    # a non locking manner.
    db.connections.close_all()
    processes = []
    for account in accounts:
        p = Process(target=analyze_account, args=(analysis_list, account, rebase_logs, from_block, to_block, from_block_time, to_block_time, ))
        p.start()
        processes.append(p)
    for p in processes:
        p.join()

def analyze_account(analysis_list, address, rebase_logs, from_block, to_block, from_block_time, to_block_time, project=OriginTokens.OUSD):
    (transaction_history, previous_transfer_logs, token_balance, pre_curve_campaign_transfer_logs, post_curve_campaign_transfer_logs) = ensure_transaction_history(address, rebase_logs, from_block, to_block, from_block_time, to_block_time, project=project)

    if project == OriginTokens.OUSD:
        is_holding_ousd = token_balance > 0.1
        is_holding_more_than_100_ousd = token_balance > 100
        is_new_account = len(previous_transfer_logs) == 0
        is_new_after_curve_start = len(pre_curve_campaign_transfer_logs) == 0
        new_after_curve_and_hold_more_than_100 = is_holding_more_than_100_ousd and is_new_after_curve_start
        non_rebase_balance_diff = 0

        for tansfer_log in filter(lambda log: isinstance(log, transfer_log), transaction_history):
            non_rebase_balance_diff += tansfer_log.amount

        analysis_list.append(
            address_analytics(is_holding_ousd, is_holding_more_than_100_ousd, is_new_account, non_rebase_balance_diff > 0, non_rebase_balance_diff < 0, is_new_after_curve_start, new_after_curve_and_hold_more_than_100)
        )
    else:
        is_holding_oeth = token_balance > 0.0001 # 0.0001 OETH or more
        is_holding_more_than_dot1_oeth = token_balance > 0.1 # 0.1 OETH or more
        is_new_account = len(previous_transfer_logs) == 0
        non_rebase_balance_diff = 0

        for tansfer_log in filter(lambda log: isinstance(log, transfer_log), transaction_history):
            non_rebase_balance_diff += tansfer_log.amount

        analysis_list.append(
            oeth_address_analytics(is_holding_oeth, is_holding_more_than_dot1_oeth, is_new_account, non_rebase_balance_diff > 0, non_rebase_balance_diff < 0)
        )


# start_time and end_time might seem redundant, but are needed so we can query the transfer logs
def ensure_analyzed_transactions(from_block, to_block, start_time, end_time, account='all', project=OriginTokens.OUSD):
    tx_query = Q()
    tran_query = Q(project=project)
    if account != 'all':
        tx_query &= Q(from_address=account) | Q(to_address=account)
        tran_query &= Q(from_address=account) | Q(to_address=account)
    # info regarding all blocks should be present
    if from_block is not None:
        tx_query &= Q(block_number__gte=from_block)
        tx_query &= Q(block_number__lt=to_block)
        tran_query &= Q(block_time__gte=start_time)
        tran_query &= Q(block_time__lt=end_time)

    transactions = Transaction.objects.filter(tx_query)
    transfer_transactions = map(lambda transfer: transfer.tx_hash, TokenTransfer.objects.filter(tran_query))

    analyzed_transactions = []
    analyzed_transaction_hashes = []

    def process_transaction(transaction):
        if transaction.tx_hash in analyzed_transaction_hashes:
            # transaction already analyzed skipping
            return

        logs = Log.objects.filter(transaction_hash=transaction.tx_hash)
        account_starting_tx = transaction.receipt_data["from"]
        contract_address = transaction.receipt_data.get("to")
        internal_transactions = transaction.internal_transactions
        received_eth = len(list(filter(lambda tx: tx["to"] == account and float(tx["value"]) > 0, internal_transactions))) > 0
        sent_eth = transaction.data['value'] != '0x0'
        transfer_origin_token_out = False
        transfer_origin_token_in = False
        transfer_coin_out = False
        transfer_coin_in = False
        origin_token_transfer_from = None
        origin_token_transfer_to = None
        origin_token_transfer_amount = None
        transfer_log_count = 0

        for log in logs:
            if log.topic_0 == TRANSFER:
                transfer_log_count += 1
                is_origin_token = (log.address == OUSD and project == OriginTokens.OUSD) or (log.address == OETH and project == OriginTokens.OETH) or (log.address == WOUSD and project == OriginTokens.WOUSD) or (log.address == WOETH and project == OriginTokens.WOETH)
                from_address = "0x" + log.topic_1[-40:]
                to_address = "0x" + log.topic_2[-40:]

                if is_origin_token:
                    origin_token_transfer_from = from_address
                    origin_token_transfer_to = to_address
                    origin_token_transfer_amount = int(slot(log.data, 0), 16) / E_18

                if account != 'all':
                    if from_address == account:
                        if is_origin_token:
                            transfer_origin_token_out = True
                        else:
                            transfer_coin_out = True
                    if to_address == account:
                        if is_origin_token:
                            transfer_origin_token_in = True
                        else:
                            transfer_coin_in = True

        classification = 'unknown'
        if account != 'all':
            swap_receive_origin_token = transfer_origin_token_in and (transfer_coin_out or sent_eth)
            swap_send_origin_token = transfer_origin_token_out and (transfer_coin_in or received_eth)

            if transfer_log_count > 0:
                if transfer_origin_token_in:
                    classification = 'transfer_in'
                elif transfer_origin_token_out:
                    classification = 'transfer_out'
                else:
                    classification = 'unknown_transfer'

            if swap_receive_origin_token:
                if project == OriginTokens.OUSD:
                    classification = 'swap_gain_ousd'
                elif project == OriginTokens.OETH:
                    classification = 'swap_gain_oeth'
                elif project == OriginTokens.WOUSD:
                    classification = 'swap_gain_wousd'
                elif project == OriginTokens.WOETH:
                    classification = 'swap_gain_woeth'
                else:
                    raise Exception('Unexpected project id', project)
            elif swap_send_origin_token:
                if project == OriginTokens.OUSD:
                    classification = 'swap_give_ousd'
                elif project == OriginTokens.OETH:
                    classification = 'swap_give_oeth'
                elif project == OriginTokens.WOUSD:
                    classification = 'swap_give_wousd'
                elif project == OriginTokens.WOETH:
                    classification = 'swap_give_woeth'
                else:
                    raise Exception('Unexpected project id', project)

        analyzed_transaction_hashes.append(transaction.tx_hash)
        analyzed_transactions.append(transaction_analysis(
            account_starting_tx,
            transaction.tx_hash,
            contract_address,
            internal_transactions,
            received_eth,
            sent_eth,
            transfer_origin_token_out,
            transfer_origin_token_in,
            transfer_coin_out,
            transfer_coin_in,
            origin_token_transfer_from,
            origin_token_transfer_to,
            origin_token_transfer_amount,
            transfer_log_count,
            classification,
            project=project
        ))

    for transaction in transactions:
        process_transaction(transaction)

    for transaction in transfer_transactions:
        process_transaction(transaction)

    return analyzed_transactions

def do_transaction_analytics(from_block, to_block, start_time, end_time, account='all', project=OriginTokens.OUSD):
    report = {
        'contracts_swaps': {},
        'contracts_other': {}
    }
    analyzed_transactions = ensure_analyzed_transactions(from_block, to_block, start_time, end_time, account, project=project)

    for analyzed_tx in analyzed_transactions:

        tx_hash, contract_address, received_eth, sent_eth, transfer_origin_token_out, transfer_origin_token_in, transfer_coin_out, transfer_coin_in, origin_token_transfer_from, origin_token_transfer_amount, transfer_log_count, classification, project = attrgetter('tx_hash', 'contract_address', 'received_eth', 'sent_eth', 'transfer_origin_token_out', 'transfer_origin_token_in', 'transfer_coin_out', 'transfer_coin_in', 'origin_token_transfer_from', 'origin_token_transfer_amount', 'transfer_log_count', 'classification', 'project')(analyzed_tx)

        is_swap_tx = classification in ('swap_gain_ousd', 'swap_give_ousd', 'swap_gain_oeth', 'swap_give_oeth')

        if (transfer_log_count > 1 or sent_eth or received_eth) and (not is_swap_tx):
            print("Transaction needing further investigating hash: {}, transfer log count: {}, sent eth: {} received eth: {} coin in: {} coin out: {} origin_token in: {} origin_token out: {}".format(tx_hash, transfer_log_count, sent_eth, received_eth, transfer_coin_out, transfer_coin_out, transfer_origin_token_in, transfer_origin_token_out))

        report_key = "contracts_swaps" if is_swap_tx else "contracts_other"
        contract_data = report[report_key][contract_address] if contract_address in report[report_key] else {
            "address": contract_address,
            "name": CONTRACT_ADDR_TO_NAME[contract_address] if contract_address in CONTRACT_ADDR_TO_NAME else "N/A",
            "total_swaps": 0,
            "total_origin_token_swapped": 0,
            "total_transactions": 0
        }

        contract_data["total_transactions"] += 1
        if origin_token_transfer_amount is not None:
            contract_data["total_swaps"] += 1
            contract_data["total_origin_token_swapped"] += origin_token_transfer_amount

        report[report_key][contract_address] = contract_data

    for report_key in ["contracts_swaps", "contracts_other"]:
        report_data = report[report_key]
        sort_key = "total_origin_token_swapped" if report_key == "contracts_swaps" else "total_swaps"

        sum_total_origin_token_swapped = 0
        for origin_token_swapped in map(lambda report_item: report_item[1]["total_origin_token_swapped"], report_data.items()):
            sum_total_origin_token_swapped += origin_token_swapped

        for contract_address, contract_data in report_data.items():
            contract_data["total_swapped_origin_token_share"] = contract_data["total_origin_token_swapped"] / sum_total_origin_token_swapped if sum_total_origin_token_swapped > 0 else 0

        report_data = {k: v for k, v in sorted(report_data.items(), key=lambda item: -item[1][sort_key])}
        report[report_key] = report_data

    return json.dumps(report)

def get_rebase_logs(from_block, to_block, project=OriginTokens.OUSD) -> List[Log]:
    contract_address = OUSD if project == OriginTokens.OUSD else OETH
    # we use distinct to mitigate the problem of possibly having double logs in database
    if from_block is None and to_block is None:
        old_logs = Log.objects.filter(
            topic_0=OUSD_TOTAL_SUPPLY_UPDATED_TOPIC,
            address=contract_address
        ).order_by('transaction_hash').distinct('transaction_hash')
        new_logs = Log.objects.filter(
            topic_0=OUSD_TOTAL_SUPPLY_UPDATED_HIGHRES_TOPIC,
            address=contract_address
        ).order_by('transaction_hash').distinct('transaction_hash')
    else:
        old_logs = Log.objects.filter(
            topic_0=OUSD_TOTAL_SUPPLY_UPDATED_TOPIC,
            address=contract_address,
            block_number__gte=from_block,
            block_number__lte=to_block
        ).order_by('transaction_hash').distinct('transaction_hash')
        new_logs = Log.objects.filter(
            topic_0=OUSD_TOTAL_SUPPLY_UPDATED_HIGHRES_TOPIC,
            address=contract_address,
            block_number__gte=from_block,
            block_number__lte=to_block
        ).order_by('transaction_hash').distinct('transaction_hash')

    rebase_logs_old = list(map(lambda log: rebase_log(log.block_number, log.transaction_index, explode_log_data(log.data)[2], log.transaction_hash), old_logs))
    rebase_logs_new = list(map(lambda log: rebase_log(log.block_number, log.transaction_index, explode_log_data(log.data)[2] / 10 ** 9, log.transaction_hash), new_logs))
    rebase_logs = rebase_logs_old + rebase_logs_new

    block_numbers = list(map(lambda rebase_log: rebase_log.block_number, rebase_logs))

    blocks = list(map(lambda block: (block.block_time, block.block_number), Block.objects.filter(block_number__in=block_numbers)))
    block_lookup = dict((y, x) for x, y in blocks)

    def map_logs(log):
        log.set_block_time(block_lookup[log.block_number])
        return log

    rebase_logs = list(map(map_logs, rebase_logs))

    # rebase logs sorted by block number descending
    rebase_logs.sort(key=lambda rebase_log: -rebase_log.block_number)
    return rebase_logs


# returns a list of transfer_logs where amount is a positive number if account received OUSD
# and a negative one if OUSD was sent from the account
def get_transfer_logs(account, from_block_time, to_block_time, project=OriginTokens.OUSD):
    if from_block_time is None and to_block_time is None:
        transfer_logs = TokenTransfer.objects.filter((Q(from_address=account) | Q(to_address=account)) & Q(project=project))
    else:
        transfer_logs = TokenTransfer.objects.filter((Q(from_address=account) | Q(to_address=account)) & Q(block_time__gte=from_block_time) & Q(block_time__lt=to_block_time) & Q(project=project))

    return list(map(lambda log: transfer_log(
        log.tx_hash.block_number,
        # for now the transaction_index (index of tx execution within a block) is not
        # available in the db yet. Will need to add a new `transaction_index` field to ousd_transfers
        # and recalculate historical data.
        0,
        log.tx_hash,
        log.amount if log.to_address.lower() == account.lower() else -log.amount,
        log.from_address,
        log.to_address,
        log.block_time,
        log.log_index
    ), transfer_logs))

def get_history_for_address(address, transaction_filter, project=OriginTokens.OUSD):
    rebase_logs = get_rebase_logs(None, None, project=project)
    hash_to_classification = dict((ana_tx.tx_hash, ana_tx.classification) for ana_tx in ensure_analyzed_transactions(None, None, None, None, address, project=project))

    (tx_history, ___, ____, _____, ______) = ensure_transaction_history(address, rebase_logs, None, None, None, None, True, project=project)

    if len(tx_history) == 0:
        return []

    if transaction_filter != None:
        transaction_filter = transaction_filter.replace('swap_ousd', 'swap_gain_ousd swap_give_ousd')
        transaction_filter = transaction_filter.replace('swap_oeth', 'swap_gain_oeth swap_give_oeth')
        transaction_filter = transaction_filter.replace('swap_wousd', 'swap_gain_wousd swap_give_wousd')
        transaction_filter = transaction_filter.replace('swap_woeth', 'swap_gain_woeth swap_give_woeth')
    tx_history_filtered = []

    # find last non rebase transaction, and remove later transactions
    last_non_yield_tx_idx = -1
    for i in range(len(tx_history) - 1, -1, -1):
        if not isinstance(tx_history[i], rebase_log):
            last_non_yield_tx_idx = i
            break;

    for i in range(0, (last_non_yield_tx_idx + 1) if last_non_yield_tx_idx != -1 else 1, 1):
        if isinstance(tx_history[i], rebase_log):
            if project != OriginTokens.WOUSD and project != OriginTokens.WOETH:
                if transaction_filter == None or 'yield' in transaction_filter:
                    tx_history_filtered.append({
                        'block_number': tx_history[i].block_number,
                        'time': tx_history[i].block_time,
                        'balance': "{:.18f}".format(float(tx_history[i].balance)),
                        'tx_hash': tx_history[i].tx_hash,
                        'amount': "{:.18f}".format(float(tx_history[i].amount)),
                        'type': 'yield'
                    })
        else:
            tx_hash = tx_history[i].tx_hash.tx_hash
            tx_classification = hash_to_classification[tx_hash] if tx_hash in hash_to_classification else 'unknown_transaction_not_found'
            if transaction_filter == None or tx_classification in transaction_filter:
                tx_history_filtered.append({
                    'block_number': tx_history[i].block_number,
                    'time': tx_history[i].block_time,
                    'balance': "{:.18f}".format(float(tx_history[i].balance)),
                    'tx_hash': tx_hash,
                    'amount': "{:.18f}".format(float(tx_history[i].amount)),
                    'from_address': tx_history[i].from_address,
                    'to_address': tx_history[i].to_address,
                    'log_index' : tx_history[i].log_index,
                    'type': tx_classification
                })

    return list(tx_history_filtered)

# when rebase logs are available enrich transfer logs with the active credits_per_token values
def enrich_transfer_logs(logs):
    # order by ascending block number for convenience
    logs.reverse()
    logs_length = len(logs)
    current_credits_per_token = 0

    # TODO: ideally there would always be one rebase transaction before transfer once since the rebase
    # tells us the correct value of credits_per_token at the time of the transfer transaction.
    # So when transfer is the first transaction we find the closest rebase transaction and use those
    # credits per token. Which is not correct...

    # find first credits per token
    for x in range(0, logs_length):
        log = logs[x]
        if isinstance(log, rebase_log):
            current_credits_per_token = Decimal(log.credits_per_token)
            break;

    for x in range(0, logs_length):
        log = logs[x]
        if isinstance(log, rebase_log):
            current_credits_per_token = Decimal(log.credits_per_token)
        elif isinstance(log, transfer_log):
            log.credits_per_token = current_credits_per_token
            logs[x] = log
        else:
            raise Exception('Unexpected object instance', log)

    # reverse back
    logs.reverse()
    return logs

def calculate_balance(credits, credits_per_token):
    if credits == 0 or credits_per_token == 0:
        return Decimal(0)
    return credits / credits_per_token

def ensure_origin_token_balance(credit_balance, logs):
    def find_previous_rebase_log(current_index, logs):
        current_index += 1
        while(current_index < len(logs)):
            log = logs[current_index]
            if isinstance(log, rebase_log):
                return log
            current_index += 1
        return None

    for x in range(0, len(logs)):
        log = logs[x]
        if isinstance(log, rebase_log):
            log.balance = calculate_balance(credit_balance, Decimal(log.credits_per_token))
            previous_log = find_previous_rebase_log(x, logs)
            if previous_log is not None:
                prev_balance = calculate_balance(credit_balance, Decimal(previous_log.credits_per_token))
                log.amount = log.balance - prev_balance
            else:
                log.amount = 0
        elif isinstance(log, transfer_log):
            log.balance = calculate_balance(credit_balance, Decimal(log.credits_per_token))
            # multiply token balance change and credits per token at the time of the event
            credit_change = - log.amount * log.credits_per_token
            credit_balance += credit_change
        else:
            raise Exception('Unexpected object instance', log)
        logs[x] = log
    return logs


def send_report_email(summary, report, prev_report, report_type, recipient_override=None):
    report.transaction_report = json.loads(str(report.transaction_report))
    if recipient_override is not None:
        e = Email(summary, render_to_string('analytics_report_v2_email.html', {
            'type': report_type,
            'report': report,
            'prev_report': prev_report,
            'change': calculate_report_change(report, prev_report),
            'stats': report_stats,
            'stat_keys': report_stats.keys(),
            'curve_stats': curve_report_stats,
            'curve_stat_keys': curve_report_stats.keys(),
            'oeth_stats': oeth_report_stats,
            'oeth_stat_keys': oeth_report_stats.keys(),
            'email': recipient_override,
            'conf_num': '',
            'is_monthly': report.month is not None
        }))
        e.execute([recipient_override])
        return
    send_report_email_core(summary, report, prev_report, report_type)
    subscribers = Subscriber.objects.filter(confirmed=True, unsubscribed=False).exclude(email=settings.CORE_TEAM_EMAIL)
    for subscriber in subscribers:
        e = Email(summary, render_to_string('analytics_report_v2_email.html', {
            'type': report_type,
            'report': report,
            'prev_report': prev_report,
            'change': calculate_report_change(report, prev_report),
            'stats': report_stats,
            'stat_keys': report_stats.keys(),
            'curve_stats': curve_report_stats,
            'curve_stat_keys': curve_report_stats.keys(),
            'oeth_stats': oeth_report_stats,
            'oeth_stat_keys': oeth_report_stats.keys(),
            'email': subscriber.email,
            'conf_num': subscriber.conf_num,
            'is_monthly': report.month is not None
        }))
        if subscriber.email is not None:
            e.execute([subscriber.email])


def send_report_email_core(summary, report, prev_report, report_type):
    core = settings.CORE_TEAM_EMAIL
    e = Email(summary, render_to_string('analytics_report_v2_email.html', {
        'type': report_type,
        'report': report,
        'prev_report': prev_report,
        'change': calculate_report_change(report, prev_report),
        'stats': report_stats,
        'stat_keys': report_stats.keys(),
        'curve_stats': curve_report_stats,
        'curve_stat_keys': curve_report_stats.keys(),
        'oeth_stats': oeth_report_stats,
        'oeth_stat_keys': oeth_report_stats.keys(),
        'email': core,
        'conf_num': 0,
        'is_monthly': report.month is not None,
    }))
    e.execute([core])


def send_weekly_email(recipient_override=None):
    weekly_reports = AnalyticsReport.objects.filter(week__isnull=False).order_by("-year", "-week")
    subject = 'Origin DeFi Analytics Weekly Report'
    send_report_email(subject, weekly_reports[0], weekly_reports[1], "Weekly", recipient_override=recipient_override)

def send_monthly_email(recipient_override=None):
    monthly_reports = AnalyticsReport.objects.filter(month__isnull=False).order_by("-year", "-month")
    subject = 'Origin DeFi Analytics Monthly Report'
    send_report_email(subject, monthly_reports[0], monthly_reports[1], "Monthly", recipient_override=recipient_override)

def ensure_transaction_history(account, rebase_logs, from_block, to_block, from_block_time, to_block_time, ignore_curve_data=False, project=OriginTokens.OUSD):
    if rebase_logs is None:
        rebase_logs = get_rebase_logs(from_block, to_block, project=project)

    if from_block_time is None and to_block_time is None:
        transfer_logs = get_transfer_logs(account, None, None, project=project)
        previous_transfer_logs = []
    else:
        transfer_logs = get_transfer_logs(account, from_block_time, to_block_time, project=project)
        previous_transfer_logs = get_transfer_logs(account, START_OF_EVERYTHING_TIME, from_block_time, project=project)

    credit_balance, credits_per_token = creditsBalanceOf(account, to_block if to_block is not None else 'latest', project=project)

    pre_curve_campaign_transfer_logs = []
    post_curve_campaign_transfer_logs = []
    if project == OriginTokens.OUSD and not ignore_curve_data:
        pre_curve_campaign_transfer_logs = get_transfer_logs(account, START_OF_EVERYTHING_TIME, START_OF_CURVE_CAMPAIGN_TIME, project)
        post_curve_campaign_transfer_logs = get_transfer_logs(account, START_OF_CURVE_CAMPAIGN_TIME, to_block_time, project)

    token_balance = calculate_balance(credit_balance, credits_per_token)

    # filter out transactions that happened before the OUSD relaunch
    balance_logs = list(filter(lambda balance_log: balance_log.block_number > START_OF_OUSD_V2, list(transfer_logs + rebase_logs)))

    # sort transfer and rebase logs by block number descending
    balance_logs.sort(key=lambda log: (-log.block_number, -log.position))
    balance_logs = enrich_transfer_logs(balance_logs)
    return (ensure_origin_token_balance(credit_balance, balance_logs), previous_transfer_logs, token_balance, pre_curve_campaign_transfer_logs, post_curve_campaign_transfer_logs)
    
def _daily_rows(steps, latest_block_number, project, start_at=0):
    # Blocks to display
    # ...this could be a bit more efficient if we pre-loaded the days and blocks in
    # on transaction, then only ensured the missing ones.
    block_numbers = [latest_block_number]  # Start with today so far
    today = datetime.utcnow()
    if today.hour < 8:
        # No rebase guaranteed yet on this UTC day
        today = (today - timedelta(seconds=24 * 60 * 60)).replace(
            tzinfo=timezone.utc
        )
    selected = datetime(today.year, today.month, today.day).replace(
        tzinfo=timezone.utc
    )

    if start_at != 0:
        block_numbers = []
        selected = (
            selected - timedelta(seconds=24 * 60 * 60 * start_at)
        ).replace(tzinfo=timezone.utc)

    for i in range(start_at, steps + 1):
        day = ensure_day(selected)
        if day is not None:
            block_numbers.append(day.block_number)
        selected = (
            selected - timedelta(seconds=24 * 60 * 60)
        ).replace(tzinfo=timezone.utc)

    START_OF_PROJECT = START_OF_OUSD_V2 if project == OriginTokens.OUSD else START_OF_OETH

    # Deduplicate list and preserving order.
    # Sometimes latest_block_number supplied to the function and latest day block_number are the same block
    # Triggering division by 0 in the code below
    block_numbers = list(filter(lambda x: x >= START_OF_PROJECT, dict.fromkeys(block_numbers)))
    block_numbers.reverse()

    # Snapshots for each block
    rows = []
    last_snapshot = None
    for block_number in block_numbers:
        if block_number < START_OF_PROJECT:
            continue
        block = ensure_block(block_number)
        s = ensure_supply_snapshot(block_number, project)
        if s is None:
            continue
        s.block_number = block_number
        s.block_time = block.block_time
        s.effective_day = (
            block.block_time - timedelta(seconds=24 * 60 * 60)
        ).replace(tzinfo=timezone.utc)
        if last_snapshot:

            contract_address = OUSD_VAULT if project == OriginTokens.OUSD else OETH_VAULT

            rebase_logs = get_rebase_logs(last_snapshot.block_number, block_number, project)
            s.rebase_events = []
            for event in rebase_logs:
                rebase_amount = 0
                rebase_fee = 0

                yield_distribution_events = Log.objects.filter(
                    topic_0=SIG_EVENT_YIELD_DISTRIBUTION,
                    address=contract_address,
                    transaction_hash=event.tx_hash
                )

                for yield_distribution_event in yield_distribution_events:
                    _, rebase_amount, rebase_fee = decode_single(
                        "(address,uint256,uint256)",
                        decode_hex(yield_distribution_event.data)
                    )              
                    
                    s.rebase_events.append({
                        'amount': (rebase_amount - rebase_fee) / 1e18,
                        'fee': rebase_fee / 1e18,
                        'tx_hash': event.tx_hash,
                        'block_number': event.block_number,
                        'block_time': event.block_time,
                    })

            blocks = s.block_number - last_snapshot.block_number
            if last_snapshot.rebasing_credits_per_token == 0:
                change = Decimal(0)
            else:
                # other_change = 1 - (s.rebasing_credits_per_token / last_snapshot.rebasing_credits_per_token)
                change = Decimal(sum(event['amount'] for event in s.rebase_events)) / (s.computed_supply - s.non_rebasing_supply)

                
            s.apr = (
                Decimal(100) * change * Decimal(365)
            )
            s.apy = to_apy(s.apr, 1)

            otoken = ensure_asset("OUSD" if project == OriginTokens.OUSD else "OETH", s.block_number, project)
            amo_supply = otoken.get_strat_holdings("ousd_metastrat" if project == OriginTokens.OUSD else "oeth_curve_amo")

            try:
                s.unboosted = to_apy(
                    (s.computed_supply - s.non_rebasing_supply)
                    / (s.computed_supply - amo_supply)
                    * s.apr,
                    1,
                )
            # If there is no non-rebasing supply, the above will divide by zero.
            except (DivisionByZero, InvalidOperation):
                s.unboosted = Decimal(0)
            s.gain = change * (s.computed_supply - s.non_rebasing_supply)
            s.fees = Decimal(sum(event['fee'] for event in s.rebase_events))

        rows.append(s)
        last_snapshot = s
    rows.reverse()
    # drop last row with incomplete information
    rows = rows[:-1]
    if len(rows) > 0 and start_at == 0:
        # Add dripper funds to today so far
        rows[0].gain += dripper_available(project=project)
    return rows


def _daily_rows_past(steps, latest_block_time, project=OriginTokens.OUSD):
    block_numbers = []
    today = datetime.utcnow()
    if today.hour < 8:
        today = (today - timedelta(seconds=24 * 60 * 60)).replace(
            tzinfo=timezone.utc
        )
    selected = datetime(latest_block_time.year, latest_block_time.month, latest_block_time.day).replace(
        tzinfo=timezone.utc
    )
    for i in range(0, steps + 1):
        day = ensure_day(selected)
        if day is not None:
            block_numbers.append(day.block_number)
        selected = (
            selected - timedelta(seconds=24 * 60 * 60)
        ).replace(tzinfo=timezone.utc)
    block_numbers = list(dict.fromkeys(block_numbers))
    block_numbers.reverse()

    rows = []
    last_snapshot = None
    for block_number in block_numbers:
        if block_number < START_OF_OUSD_V2:
            continue
        block = ensure_block(block_number)
        s = ensure_supply_snapshot(block_number, project=project)
        s.block_number = block_number
        s.block_time = block.block_time
        if last_snapshot:
            change = (
                (
                    s.rebasing_credits_per_token
                    / last_snapshot.rebasing_credits_per_token
                )
                - Decimal(1)
            ) * -1
            s.gain = change * (s.computed_supply - s.non_rebasing_supply)
        rows.append(s)
        last_snapshot = s
    rows.reverse()
    rows = rows[:-1]
    return rows