from core.blockchain.rpc import latest_block
from core.blockchain.harvest import reload_all

def run():
    latest = latest_block()
    reload_all(latest - 2)