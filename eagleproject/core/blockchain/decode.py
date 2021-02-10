import re
from eth_utils import add_0x_prefix, encode_hex
from eth_abi import decode_single, encode_single

SIG_PATTERN = r'^([A-Za-z_0-9]+)\(([0-9A-Za-z_,\[\]]*)\)$'


def slot(value, i):
    """Get the x 256bit field from a data string"""
    return value[2 + i * 64:2 + (i + 1) * 64]


def bytes32s_to_hex(types, args):
    """ Encode bytes32 args to hex. types array contains types matching the
    values in args
    """
    if 'bytes32' not in types:
        return args

    if type(args) == tuple:
        args = list(args)

    for i, typ in enumerate(types):
        if typ == 'bytes32':
            args[i] = encode_hex(args[i])

    return args


def encode_args(signature, args):
    """ Encode call arguments for an RPC call """
    match = re.match(SIG_PATTERN, signature)

    if not match:
        # TODO: Better way to represent this?
        return ""

    try:
        types_string = match.groups()[1]
    except IndexError:
        return ""

    if not types_string:
        return ""

    # Tag the arg types from the signature and decode calldata accordingly
    types = [x.strip() for x in types_string.split(',')]
    arg_sig = '({})'.format(','.join(types))

    if not types:
        return ""

    assert len(types) == len(args), "args do not match signature"

    return encode_single(arg_sig, args).hex()


def decode_args(signature, calldata):
    """ Decode calldata arguments for a given string signature """
    match = re.match(SIG_PATTERN, signature)

    if not match:
        # TODO: Better way to represent this?
        return None

    try:
        types_string = match.groups()[1]
    except IndexError:
        return None

    # Tag the arg types from the signature and decode calldata accordingly
    types = [x.strip() for x in types_string.split(',')]
    arg_sig = '({})'.format(','.join(types))

    return decode_single(arg_sig, calldata)


def decode_call(signature, calldata):
    """ Decode calldata for a given string signature """
    match = re.match(SIG_PATTERN, signature)

    if not match:
        # TODO: Better way to represent this?
        return '{}({})'.format(signature[:10], calldata)

    func = match.groups()[0]
    try:
        types_string = match.groups()[1]
    except IndexError:
        types_string = ""

    # Tag the arg types from the signature and decode calldata accordingly
    types = [x.strip() for x in types_string.split(',')]
    args = decode_single('({})'.format(','.join(types)), calldata)
    args = bytes32s_to_hex(types, args)

    # Assemble a human-readable function call with arg values
    return '{}({})'.format(func, ','.join([str(v) for v in args]))


def decode_calls(signatures, calldatas):
    """ Decode multiple calldatas for given string signatures """
    calls = []

    for sig, data in zip(signatures, calldatas):
        calls.append(decode_call(sig, data))

    return calls
