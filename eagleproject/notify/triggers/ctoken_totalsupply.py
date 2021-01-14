from decimal import Decimal
from statistics import mean
from core.blockchain.addresses import CONTRACT_ADDR_TO_NAME
from core.common import dict_append
from notify.events import event_critical, event_high

PERCENT_DIFF_THRESHOLD = Decimal(0.05)


def get_past_comparison(ctoken_snaps):
    """ Get the historical comparison value.  It will either be an average of
    past values, last value, or 0, depending on what is available. """

    count = len(ctoken_snaps)

    if count < 2:
        return 0

    elif count > 2:
        return mean([x.total_supply for x in ctoken_snaps[1:]])

    return ctoken_snaps[1].total_supply


def run_trigger(recent_ctoken_snapshots):
    """ Trigger on extreme supply changes in cTokens """
    events = []
    snaps = {}

    for snap in recent_ctoken_snapshots:
        dict_append(snaps, snap.address, snap)

    for ctoken_address in snaps:
        total_supply_comp = get_past_comparison(snaps[ctoken_address])
        total_supply_current = snaps[ctoken_address][0].total_supply
        diff_threshold = total_supply_comp * PERCENT_DIFF_THRESHOLD

        if total_supply_current < total_supply_comp:
            diff = total_supply_comp - total_supply_current

            if diff > diff_threshold:
                events.append(event_critical(
                    "Compound cToken Total Supply Fluctuation   🚨",
                    "The cToken {} has dropped more than {}% between "
                    "snapshots. This could indicate issues or a rush on "
                    "capital.".format(
                        CONTRACT_ADDR_TO_NAME.get(
                            ctoken_address,
                            ctoken_address
                        ),
                        round(PERCENT_DIFF_THRESHOLD * Decimal(100))
                    )
                ))

        else:
            diff = total_supply_current - total_supply_comp

            if diff > diff_threshold:
                events.append(event_high(
                    "Compound cToken Total Supply Fluctuation   🚨",
                    "The cToken {} has gained more than {}% between "
                    "snapshots.".format(
                        CONTRACT_ADDR_TO_NAME.get(
                            ctoken_address,
                            ctoken_address
                        ),
                        round(PERCENT_DIFF_THRESHOLD * Decimal(100))
                    )
                ))

    return events
