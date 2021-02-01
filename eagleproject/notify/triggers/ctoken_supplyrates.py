from decimal import Decimal
from core.blockchain.addresses import CONTRACT_ADDR_TO_NAME
from notify.events import event_low

HIGH_RATE = Decimal(0.15)  # 15%
LOW_RATE = Decimal(0.03)  # 3%


def run_trigger(ctoken_snapshots):
    """ Trigger on remarkable interest rates """
    events = []

    for snap in ctoken_snapshots:
        if snap.supply_apy > HIGH_RATE:
            events.append(event_low(
                "Compound Supply Rate   📈",
                "The cToken {} has an unusually high supply APY of {}%".format(
                    CONTRACT_ADDR_TO_NAME.get(
                        snap.address,
                        snap.address
                    ),
                    round(snap.supply_apy * Decimal(100), 2)
                ),
                block_number=snap.block_number
            ))

        elif snap.supply_apy < LOW_RATE:
            events.append(event_low(
                "Compound Supply Rate   📉",
                "The cToken {} has an unusually low supply APY of {}%".format(
                    CONTRACT_ADDR_TO_NAME.get(
                        snap.address,
                        snap.address
                    ),
                    round(snap.supply_apy * Decimal(100), 2)
                ),
                block_number=snap.block_number
            ))

    return events
