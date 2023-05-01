from core.blockchain.rpc import latest_block
from core.blockchain.harvest import refresh_transactions

def run():
    latest = latest_block()
    refresh_transactions(latest - 2)
