from core.blockchain.rpc import latest_block
from core.blockchain.harvest import snap

def run():
    latest = latest_block()
    snap(latest - 2)