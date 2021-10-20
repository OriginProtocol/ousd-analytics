import requests
from django.conf import settings

ETHERSCAN_ENDPOINT = "https://api.etherscan.io/api"
DAILY_BLOCKS = 5760 // (24 * 60 * 60) / 15


def get_contract_transactions(address, from_block, end_block):
    """ Get all transactions for an account """
    action = "txlist"

    uri = (
        "{}?module=account&action={}&address={}&startblock={}&endblock={}"
        "&sort=desc&apikey={}".format(
            ETHERSCAN_ENDPOINT,
            action,
            address,
            from_block,
            end_block,
            settings.ETHERSCAN_API_KEY,
        )
    )

    r = requests.get(uri)

    if r.status_code != 200:
        raise Exception(
            "Failed to fetch ({}) transaction list from Etherscan".format(
                r.status_code
            )
        )

    return r.json().get("result")

def get_internal_txs_bt_txhash(txhash):
    uri = (
        "{}?module=account&action=txlistinternal&txhash={}&apikey={}".format(
            ETHERSCAN_ENDPOINT,
            txhash,
            settings.ETHERSCAN_API_KEY,
        )
    )

    r = requests.get(uri)

    if r.status_code != 200:
        raise Exception(
            "Failed to fetch ({}) internal transactions from Etherscan for transaction: {}".format(
                r.status_code,
                txhash
            )
        )

    json = r.json()
    # no transactions found
    if json.get("status") == '0':
        return []
    elif json.get("status") == '1':
        return json.get("result")
    else: 
        print("Unexpected status returned: {} for transaction: {}".format(json.get("status"), txhash))
        return []
