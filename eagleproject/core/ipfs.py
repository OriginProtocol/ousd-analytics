import requests

from core.logging import get_logger

log = get_logger(__name__)


def fetch_ipfs_json(ipfs_hash):
    """ Fetch a JSON IPFS object """
    if not ipfs_hash:
        return {}

    r = requests.get('https://ipfs.io/ipfs/{}'.format(ipfs_hash))

    if r.status_code != 200:
        log.error('Failed to fetch file from IPFS: {}'.format(ipfs_hash))
        return {}

    return r.json()


def strip_terrible_ipfs_prefix(v):
    """ Curve Aragon voting uses IPFS hashes stored in their contract events
    that are formatted like:

        `ipfs:Qmb3zSLiiNKVn48RYD6pcAcmTS3SVcKTLtKhXNLTuTH8gt`

    I have no idea why, this is ridiculous.
    """
    if v.startswith('ipfs:Qm'):
        return v[5:]
    return v
