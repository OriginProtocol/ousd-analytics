from core.blockchain.harvest.transaction_history import backfill_transactions

def run(*script_args):
    project = script_args[0] if len(script_args) > 0 else None
    backfill_transactions(project)