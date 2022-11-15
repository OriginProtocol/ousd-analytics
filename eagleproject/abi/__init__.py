import json
from sys import getsizeof
from eth_hash.auto import keccak
from eth_utils import add_0x_prefix, encode_hex
from eth_typing import HexStr
from pathlib import Path
from typing import Any, Dict, List, Optional

from core.logging import get_logger

log = get_logger(__name__)
ABI_DIR = Path(__file__).parent.joinpath("data")

# Singleton storage. Best to use functions below
_abis: Dict[str, List[Dict[str, Any]]] = {}
_selector_to_sig: Dict[str, str] = {}


def lazy_load_abis(func):
    """ Decorator to lazy load ABIs into memory """

    def wrappped(*args, **kwargs):
        if len(_abis) == 0:
            load_abis()

        return func(*args, **kwargs)

    return wrappped


@lazy_load_abis
def selector_to_signature(selector: str) -> Optional[str]:
    """Given a hex 4-byte selector, return a full function signature if
    available.

    >>> selector_to_signature("0x23b872dd")
    'transferFrom(address,address,uint256)'
    """
    global _selector_to_sig
    return _selector_to_sig.get(add_0x_prefix(HexStr(selector)))


def signature_from_def(def_obj: Dict[str, Any]) -> str:
    """Given a function or event definition in a JSON ABI, create a function
    signature."""
    name = def_obj["name"]
    args = [arg["type"] for arg in def_obj["inputs"]]
    return f"{name}({','.join(args)})"


def process_abi(abi: List[Dict[str, Any]]):
    """ Process the `abi` prop from a deployment file into memory """
    global _selector_to_sig

    for item in abi:
        if item.get("type") in ["event", "function"]:
            signature = signature_from_def(item)
            sig_hash = encode_hex(keccak(signature.encode("utf-8")))
            selector = sig_hash[:10]  # 4 hex bytes plus hex prefix
            _selector_to_sig[selector] = signature


def load_abis():
    """ Load the ABIs from the data files into memory """
    for fil in ABI_DIR.iterdir():
        if fil.name.endswith(".abi.json"):
            # We know it ends with the above 9 chars
            contract = fil.name[:-9]
            abi = json.loads(fil.read_text())
            _abis[contract] = abi

            process_abi(_abis[contract])

    log.info(f"Loaded {getsizeof(_abis)} bytes of ABIs")
    log.info(f"Stored {getsizeof(_selector_to_sig)} bytes of signature lookups")
