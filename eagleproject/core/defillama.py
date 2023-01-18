import requests

from core.logging import get_logger

log = get_logger(__name__)

DEFILLAMA_ENDPOINT = "https://stablecoins.llama.fi"

def get_stablecoin_market_cap():
    
    uri = "{}/stablecoincharts/all".format(
        DEFILLAMA_ENDPOINT,
    )

    log.debug("Fetching stablecoin market cap data from {}".format(uri))

    r = requests.get(uri)

    if r.status_code != 200:
        raise Exception(
            "Failed to fetch ({}) stablecoin market cap list from Defi Llama".format(
                r.status_code
            )
        )

    return r.json()
