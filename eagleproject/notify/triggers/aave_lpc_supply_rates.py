from decimal import Decimal
from core.blockchain.addresses import CONTRACT_ADDR_TO_NAME
from notify.events import event_low

HIGH_RATE = Decimal(0.15)  # 15%
LOW_RATE = Decimal(0.03)  # 3%


def run_trigger(aave_reserve_snapshots):
    """ Trigger on remarkable interest rates """
    events = []

    for snap in aave_reserve_snapshots:
        if snap.current_liquidity_rate > HIGH_RATE:
            events.append(event_low(
                "Aave Supply Rate   📈",
                "Aave {} has an unusually high supply APY of {}%".format(
                    CONTRACT_ADDR_TO_NAME.get(
                        snap.asset,
                        snap.asset
                    ),
                    round(snap.current_liquidity_rate * Decimal(100), 2)
                ),
                block_number=snap.block_number
            ))

        elif snap.current_liquidity_rate < LOW_RATE:
            events.append(event_low(
                "Aave Supply Rate   📉",
                "Aave {} has an unusually low supply APY of {}%".format(
                    CONTRACT_ADDR_TO_NAME.get(
                        snap.asset,
                        snap.asset
                    ),
                    round(snap.current_liquidity_rate * Decimal(100), 2)
                ),
                block_number=snap.block_number
            ))

    return events
