from decimal import Decimal

from core.common import format_decimal
from core.logging import get_logger

from notify.events import event_critical, event_high, event_low

from core.blockchain.strategies import STRATEGIES

log = get_logger(__name__)

ASSET_BLOCK_SYMBOLS = ["DAI", "USDC", "USDT", "OUSD"]
PERCENT_CRITICAL = Decimal(0.25)
PERCENT_WARNING = Decimal(0.1)
PERCENT_INFO = Decimal(0.05)

def get_recent_entries(symbol, latest_asset_blocks, last_week_asset_blocks):
    current = None
    previous = None

    last_week = None
    latest = list(latest_asset_blocks.filter(symbol=symbol)) if type(latest_asset_blocks) is not list else []
    last_week = list(last_week_asset_blocks.filter(symbol=symbol)) if type(last_week_asset_blocks) is not list else []

    if len(latest) < 1:
        log.debug("No recent asset blocks, skipping")
        return (None, None)

    elif len(latest) > 1:
        previous = latest[1]

    else:
        if len(last_week) < 1:
            log.debug("No asset blocks for last week, skipping")
            return (None, None)
        previous = last_week[-1]

    current = latest[0]

    return (current, previous)


def run_trigger(snapshot_cursor, latest_asset_blocks, last_week_asset_blocks):
    """ Template trigger """
    events = []

    for symbol in ASSET_BLOCK_SYMBOLS:
        (current, previous) = get_recent_entries(symbol, latest_asset_blocks, last_week_asset_blocks)

        if current is None or previous is None:
            continue

        current_meta_holdings = getattr(current, 'strat_holdings')
        previous_meta_holdings = getattr(previous, 'strat_holdings')

        for (prop, strat) in STRATEGIES.items():
            name = strat.get("NAME") + " Holding"

            current_holding = current.get_strat_holdings(prop)
            previous_holding = previous.get_strat_holdings(prop)

            if prop == "ousd_metastrat":
                # For OUSD MetaStrategy, assume 50%-50% split
                if symbol in ("DAI", "USDC", "USDT"):
                    current_holding = current_holding / 2
                    previous_holding = previous_holding / 2
                elif symbol == "OUSD":
                    current_total = 0
                    previous_total = 0

                    for symbol in ASSET_BLOCK_SYMBOLS:
                        (c, p) = get_recent_entries(symbol, latest_asset_blocks, last_week_asset_blocks)
                        if c is None or p is None:
                            continue
                        current_total += c.get_strat_holdings(prop)
                        previous_total += p.get_strat_holdings(prop)

                    current_holding = current_total / 2
                    current_holding = previous_total / 2

            diff = current_holding - previous_holding
            absdiff = abs(diff)

            # No change
            if absdiff < 1:
                log.debug("No change in holding, skipping")
                continue

            critical_threshold = current_holding * PERCENT_CRITICAL
            warning_threshold = current_holding * PERCENT_WARNING
            info_threshold = current_holding * PERCENT_INFO

            event_func = event_low
            threshold_percent = 0
            change_string = ""

            if absdiff > critical_threshold:
                change_string = "Large"
                if diff < 0:
                    event_func = event_critical
                threshold_percent = round(PERCENT_CRITICAL * Decimal(100))
            elif absdiff > warning_threshold:
                change_string = "Medium"
                if diff < 0:
                    event_func = event_high
                threshold_percent = round(PERCENT_WARNING * Decimal(100))
            elif absdiff > info_threshold:
                change_string = ""
                event_func = event_low
                threshold_percent = round(PERCENT_INFO * Decimal(100))

            if threshold_percent:
                events.append(event_func(
                    "{} {} {}".format(
                        change_string,
                        name,
                        'Gain' if diff > 0 else 'Loss',
                    ),
                    "OUSD Bot just saw a change of {}% in {} ({})\n\n"
                    "**Previous**: {} (block {})\n"
                    "**Current**: {} (block {})\n"
                    "**Change**: {}".format(
                        threshold_percent,
                        name,
                        symbol,
                        format_decimal(previous_holding, 4),
                        previous.block_number,
                        format_decimal(current_holding, 4),
                        current.block_number,
                        format_decimal(diff, 4),
                    )
                ))

    return events
