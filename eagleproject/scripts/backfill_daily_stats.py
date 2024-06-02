from core.blockchain.harvest.transaction_history import backfill_daily_stats

def run(*script_args):
    project = script_args[0] if len(script_args) > 0 else None
    backfill_daily_stats(project)