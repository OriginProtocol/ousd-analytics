from decimal import *
from django import db
from multiprocessing import (
    Process,
    Manager,
)

from core.models import (
    Log,
    OusdTransfer,
    Block,
    AnalyticsReport
)
from django.db.models import Q
from core.blockchain.harvest.transactions import (
    explode_log_data
)
from core.blockchain.rpc import (
    creditsBalanceOf,
)
from core.blockchain.rpc import (
    balanceOf,
)
from datetime import (
    datetime,
)

from core.blockchain.const import (
    START_OF_EVERYTHING_TIME
)

from core.blockchain.utils import (
    chunks,
)

import calendar

ACCOUNT_ANALYZE_PARALLELISM=4

class rebase_log:
    # block_number
    # credits_per_token
    # balance

    def __init__(self, block_number, credits_per_token):
        self.block_number = block_number
        self.credits_per_token = credits_per_token

    def __str__(self):
        return 'rebase log: block: {} creditsPerToken: {} balance: {}'.format(self.block_number, self.credits_per_token, self.balance if hasattr(self, 'balance') else 0)

class transfer_log:
    # block_number
    # amount
    # credits_per_token
    # balance

    def __init__(self, block_number, amount):
        self.block_number = block_number
        self.amount = amount

    def __str__(self):
        return 'transfer log: block: {} amount: {} creditsPerToken: {} balance: {}'.format(self.block_number, self.amount, self.credits_per_token if hasattr(self, 'credits_per_token') else 'N/A', self.balance if hasattr(self, 'balance') else 'N/A')

class address_analytics:
    # OUSD increasing/decreasing is ignoring rebase events
    def __init__(self, is_holding_ousd, is_holding_more_than_100_ousd, is_new_account, has_ousd_increased, has_ousd_decreased):
        self.is_holding_ousd = is_holding_ousd
        self.is_holding_more_than_100_ousd = is_holding_more_than_100_ousd
        self.is_new_account = is_new_account
        self.has_ousd_increased = has_ousd_increased
        self.has_ousd_decreased = has_ousd_decreased

    def __str__(self):
        return 'address_analytics: is_holding_ousd: {self.is_holding_ousd} is_holding_more_than_100_ousd: {self.is_holding_more_than_100_ousd} is_new_account: {self.is_new_account} has_ousd_increased: {self.has_ousd_increased} has_ousd_decreased: {self.has_ousd_decreased}'.format(self=self)

class analytics_report:
    def __init__(self, accounts_analyzed, accounts_holding_ousd, accounts_holding_more_than_100_ousd, new_accounts, accounts_with_non_rebase_balance_increase, accounts_with_non_rebase_balance_decrease):
        self.accounts_analyzed = accounts_analyzed
        self.accounts_holding_ousd = accounts_holding_ousd
        self.accounts_holding_more_than_100_ousd = accounts_holding_more_than_100_ousd
        self.new_accounts = new_accounts
        self.accounts_with_non_rebase_balance_increase = accounts_with_non_rebase_balance_increase
        self.accounts_with_non_rebase_balance_decrease = accounts_with_non_rebase_balance_decrease

    def __str__(self):
        return 'Analytics report: accounts_analyzed: {} accounts_holding_ousd: {} accounts_holding_more_than_100_ousd: {} new_accounts: {} accounts_with_non_rebase_balance_increase: {} accounts_with_non_rebase_balance_decrease: {}'.format(self.accounts_analyzed, self.accounts_holding_ousd, self.accounts_holding_more_than_100_ousd, self.new_accounts, self.accounts_with_non_rebase_balance_increase, self.accounts_with_non_rebase_balance_decrease)

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

def upsert_report(week_option, month_option, year, report, block_start_number, block_end_number, start_time, end_time):
    analyticsReport = None
    params = {
        "block_start": block_start_number,
        "block_end": block_end_number,
        "start_time": start_time,
        "end_time": end_time,
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
        "accounts_analyzed": report.accounts_analyzed,
        "accounts_holding_ousd": report.accounts_holding_ousd,
        "accounts_holding_more_than_100_ousd": report.accounts_holding_more_than_100_ousd,
        "new_accounts": report.new_accounts,
        "accounts_with_non_rebase_balance_increase": report.accounts_with_non_rebase_balance_increase,
        "accounts_with_non_rebase_balance_decrease": report.accounts_with_non_rebase_balance_decrease,
    }

    if (week_option != None):
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

def create_time_interval_report_for_previous_week(week_override):
    year_number = datetime.now().year
    # number of the week in a year - for the previous week
    week_number = week_override if week_override is not None else int(datetime.now().strftime("%W")) - 1

    if not should_create_new_report(year_number, None, week_number):
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
    report = create_time_interval_report(
        block_start_number,
        block_end_number,
        start_time,
        end_time
    )

    upsert_report(
        week_number,
        None,
        year_number,
        report,
        block_start_number, 
        block_end_number,
        start_time,
        end_time
    )

def should_create_new_report(year, month_option, week_option):
    if month_option is not None: 
        existing_report = AnalyticsReport.objects.filter(Q(year=year) & Q(month=month_option))
    elif week_option is not None: 
        existing_report = AnalyticsReport.objects.filter(Q(year=year) & Q(week=week_option))

    if len(existing_report) == 1:
        existing_report = existing_report[0]

        # nothing to do here, report is already done
        if existing_report.status == 'done':
            return False

        # in seconds
        report_age = (datetime.now() - existing_report.updated_at.replace(tzinfo=None)).total_seconds()

        # report might still be processing
        if report_age < 3 * 60 * 60:
            return False

    return True

def create_time_interval_report_for_previous_month(month_override):
    # number of the month in a year - for the previous month
    month_number = month_override if month_override is not None else int(datetime.now().strftime("%m")) - 1
    year_number = datetime.now().year + (-1 if month_number == 12 else 0)

    if not should_create_new_report(year_number, month_number, None):
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
    report = create_time_interval_report(
        block_start_number,
        block_end_number,
        start_time,
        end_time
    )

    upsert_report(
        None,
        month_number,
        year_number,
        report,
        block_start_number, 
        block_end_number,
        start_time,
        end_time
    )

# get all accounts that at some point held OUSD
def fetch_all_holders():
    to_addresses = list(map(lambda log: log['to_address'], OusdTransfer.objects.values('to_address').distinct()))
    from_addresses = list(map(lambda log: log['from_address'], OusdTransfer.objects.values('from_address').distinct()))
    return list(set(filter(lambda address: address not in ['0x0000000000000000000000000000000000000000', '0x000000000000000000000000000000000000dead'], to_addresses + from_addresses)))

def create_time_interval_report(from_block, to_block, from_block_time, to_block_time):
    decimal_context = getcontext()
    decimal_prec = decimal_context.prec
    decimal_rounding = decimal_context.rounding
    
    # to simulate uint256 in solidity when using decimals 
    decimal_context.prec = 18
    decimal_context.rounding = 'ROUND_DOWN'

    all_addresses = fetch_all_holders()

    rebase_logs = get_rebase_logs(from_block, to_block)

    manager = Manager()
    analysis_list = manager.list()

    #for chunk in chunks(all_addresses[:500], ACCOUNT_ANALYZE_PARALLELISM):
    for chunk in chunks(all_addresses, ACCOUNT_ANALYZE_PARALLELISM):
        analyze_account_in_parallel(analysis_list, chunk, rebase_logs, from_block, to_block, from_block_time, to_block_time)


    accounts_analyzed = len(analysis_list)
    accounts_holding_ousd = 0
    accounts_holding_more_than_100_ousd = 0
    new_accounts = 0
    accounts_with_non_rebase_balance_increase = 0
    accounts_with_non_rebase_balance_decrease = 0

    for analysis in analysis_list:
        accounts_holding_ousd += 1 if analysis.is_holding_ousd else 0
        accounts_holding_more_than_100_ousd += 1 if analysis.is_holding_more_than_100_ousd else 0
        new_accounts += 1 if analysis.is_new_account else 0
        accounts_with_non_rebase_balance_increase += 1 if analysis.has_ousd_increased else 0
        accounts_with_non_rebase_balance_decrease += 1 if analysis.has_ousd_decreased else 0

    report = analytics_report(
        accounts_analyzed,
        accounts_holding_ousd,
        accounts_holding_more_than_100_ousd,
        new_accounts,
        accounts_with_non_rebase_balance_increase,
        accounts_with_non_rebase_balance_decrease
    )

    # set the values back again
    decimal_context.prec = decimal_prec
    decimal_context.rounding = decimal_rounding
    return report


def analyze_account_in_parallel(analysis_list, accounts, rebase_logs, from_block, to_block, from_block_time, to_block_time):
    print("Analyzing {} accounts".format(len(accounts)))
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

def analyze_account(analysis_list, address, rebase_logs, from_block, to_block, from_block_time, to_block_time):
    (transaction_history, previous_transfer_logs, ousd_balance) = ensure_transaction_history(address, rebase_logs, from_block, to_block, from_block_time, to_block_time)

    is_holding_ousd = ousd_balance > 0.1
    is_holding_more_than_100_ousd = ousd_balance > 100
    is_new_account = len(previous_transfer_logs) == 0
    non_rebase_balance_diff = 0

    for tansfer_log in filter(lambda log: isinstance(log, transfer_log), transaction_history):
        non_rebase_balance_diff += tansfer_log.amount

    analysis_list.append(
        address_analytics(is_holding_ousd, is_holding_more_than_100_ousd, is_new_account, non_rebase_balance_diff > 0, non_rebase_balance_diff < 0)
    )

def get_rebase_logs(from_block, to_block):
    logs = Log.objects.filter(Q(topic_0="0x99e56f783b536ffacf422d59183ea321dd80dcd6d23daa13023e8afea38c3df1") & Q(block_number__gte=from_block) & Q(block_number__lte=to_block))
    rebase_logs = list(map(lambda log: rebase_log(log.block_number, explode_log_data(log.data)[2]), logs))
    # rebase logs sorted by block number descending
    rebase_logs.sort(key=lambda rebase_log: -rebase_log.block_number)
    return rebase_logs


# returns a list of transfer_logs where amount is a positive number if account received OUSD
# and a negative one if OUSD was sent from the account
def get_transfer_logs(account, from_block_time, to_block_time):
    transfer_logs = OusdTransfer.objects.filter((Q(from_address=account) | Q(to_address=account)) & Q(block_time__gte=from_block_time) & Q(block_time__lt=to_block_time))
    return list(map(lambda log: transfer_log(log.tx_hash.block_number, log.amount if log.to_address.lower() == account.lower() else -log.amount), transfer_logs))

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

def ensure_ousd_balance(credit_balance, logs):
    for x in range(0, len(logs)):
        log = logs[x]
        if isinstance(log, rebase_log):
            log.balance = calculate_balance(credit_balance, Decimal(log.credits_per_token))
        elif isinstance(log, transfer_log):
            log.balance = calculate_balance(credit_balance, Decimal(log.credits_per_token))
            # multiply token balance change and credits per token at the time of the event
            credit_change = - log.amount * log.credits_per_token
            credit_balance += credit_change
        else:
            raise Exception('Unexpected object instance', log)
        logs[x] = log
    return logs

def ensure_transaction_history(account, rebase_logs, from_block, to_block, from_block_time, to_block_time):
    if rebase_logs is None:
        rebase_logs = get_rebase_logs(from_block, to_block)

    previous_transfer_logs = get_transfer_logs(account, START_OF_EVERYTHING_TIME, from_block_time)
    transfer_logs = get_transfer_logs(account, from_block_time, to_block_time)
    credit_balance, credits_per_token = creditsBalanceOf(account, to_block)
    ousd_balance = calculate_balance(credit_balance, credits_per_token)

    balance_logs = list(transfer_logs + rebase_logs)
    # sort transfer and rebase logs by block number descending
    balance_logs.sort(key=lambda log: -log.block_number)
    balance_logs = enrich_transfer_logs(balance_logs)
    return (ensure_ousd_balance(credit_balance, balance_logs), previous_transfer_logs, ousd_balance)
    

