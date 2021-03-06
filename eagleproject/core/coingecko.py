import requests

from core.logging import get_logger

log = get_logger(__name__)

COINGECKO_ENDPOINT = "https://api.coingecko.com/api/v3"

TICKER_TO_COINGECKO_ID = {
    "OGN": "origin-protocol",
    "OUSD": "origin-dollar",
}


def get_price(ticker, currencies=["usd"]):
    """ Get all transactions for an account """
    coingecko_id = TICKER_TO_COINGECKO_ID.get(ticker)

    if not coingecko_id:
        raise ValueError("Unable to find CoinGecko ID for ticker {}".format(
            ticker
        ))

    uri = "{}{}?ids={}&vs_currencies={}".format(
        COINGECKO_ENDPOINT,
        '/simple/price',
        coingecko_id,
        ",".join(currencies),
    )

    log.debug("Fetching price data from {}".format(uri))

    r = requests.get(uri)

    if r.status_code != 200:
        raise Exception(
            "Failed to fetch ({}) price data list from CoinGecko".format(
                r.status_code
            )
        )

    return r.json().get(coingecko_id)
