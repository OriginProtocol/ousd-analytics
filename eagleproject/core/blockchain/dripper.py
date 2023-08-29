from datetime import datetime, timedelta

from core.models import OriginTokens

from core.blockchain.addresses import (
    DRIPPER,
    OETH_DRIPPER,
    USDT,
    WETH,
)

from core.blockchain.rpc import (
    balanceOf,
    dripper_available,
    dripper_drip_rate,
)

LOCAL_DRIPPER_CACHE = {
    OriginTokens.OUSD: None,
    OriginTokens.OETH: None,
}

def get_dripper_stats(project):
    global LOCAL_DRIPPER_CACHE

    cached_data = LOCAL_DRIPPER_CACHE.get(project)
    if cached_data is not None:
        valid_until, stats = cached_data
        if valid_until > datetime.today():
            return stats

    token = USDT if project == OriginTokens.OUSD else WETH
    token_decimals = 6 if project == OriginTokens.OUSD else 18
    dripper_addr = DRIPPER if project == OriginTokens.OUSD else OETH_DRIPPER

    token_balance = balanceOf(token, dripper_addr, token_decimals)
    collectable = dripper_available(project=project)
    rate = dripper_drip_rate(project=project)
    
    rate_per_minute = rate * 60
    rate_per_hour = rate * 60 * 60
    rate_per_day = rate * 24 * 60 * 60

    data = {
        "token": token,
        "drip_rate": rate,
        "rate_per_minute": rate_per_minute,
        "rate_per_hour": rate_per_hour,
        "rate_per_day": rate_per_day,
        "token_balance": token_balance,
        "collectable": collectable,
        "updated_at": datetime.today(),
    }

    LOCAL_DRIPPER_CACHE[project] = [
        # Cache stuff for 30m
        datetime.today() + timedelta(minutes=30),
        data
    ]

    return data

