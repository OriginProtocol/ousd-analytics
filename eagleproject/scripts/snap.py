from core.blockchain.rpc import latest_block
from core.blockchain.harvest import snap

def run(*script_args):
    block_number = int(script_args[0]) if len(script_args) > 0 else (latest_block() - 2)
    snap(block_number)