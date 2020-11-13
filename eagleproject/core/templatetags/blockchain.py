from django import template
from django.template.defaultfilters import stringfilter
from django.utils import timezone
from binascii import unhexlify
from decimal import Decimal
from eth_abi import decode_single
from core.blockchain import _slot
import pytz


register = template.Library()

CONTRACT_NAMES = {
    "0x277e80f3e14e7fb3fc40a9d6184088e0241034bd": "Vault",
    "0x2a8e1e676ec238d8a992307b495b45b3feaa5e86": "OUSD",
    "0xb72b3f5523851c2eb0ca14137803ca4ac7295f3f": "OUSD Internal",
    "0x3c09b440f9e46c0e4a665539aeca80fcaa92c36e": "OUSD Internal",
    "0x1ae95dd4eeae7ed03da79856c2d44ffa3318f805": "OUSD Internal",
    "0xa7f26e9aeeea4fe16d9c4a6a0464af8258f437bb": "Vault Internal1",
    "0xf251cb9129fdb7e9ca5cad097de3ea70cab9d8f9": "Vault Internal2",
    "0x0660bf15a89d8e90cba1b3f0ccf493c415b1369d": "Vault Internal3",
    "0x69a8b2ae6a3606b766be99c42328459167f51b25": "Vault Internal Admin",
    "0xaed9fdc9681d61edb5f8b8e421f5cee8d7f4b04f": "Origin Multisig",
    "0x8a5ff78bfe0de04f5dc1b57d2e1095be697be76e": "Origin Timelock",
    "0x52bebd3d7f37ec4284853fd5861ae71253a7f428": "Origin Minute Timelock",
    "0xdac17f958d2ee523a2206206994597c13d831ec7": "USDT",
    "0x6b175474e89094c44da98b954eedeac495271d0f": "DAI",
    "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48": "USDC",
    "0xb7277a6e95992041568d9391d09d0122023778a2": "USDC Internal",
    "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2": "WETH",
    "0x5d3a536e4d6dbd6114cc1ead35777bab948e3643": "cDAI",
    "0xbb8be4772faa655c255309afc3c5207aa7b896fd": "cDAI Storage",
    "0x3d9819210a31b4961b30ef54be2aed79b9c9cd3b": "Compound Comptroller",
    "0x7b5e3521a049c8ff88e6349f33044c6cc33c113c": "Compound Comptroller Internal",
    "0x39aa39c021dfbae8fac545936693ac917d5e7563": "cUSDC",
    "0xf650c3d88d12db855b8bf7d11be6c55a4e07dcc9": "cUSDT",
    "0x976aa93ca5aaa569109f4267589c619a097f001d": "cUSDT Internal",
    "0xcf67e56965ad7cec05ebf88bad798a875e0460eb": "MixOracle",  # Outdated
    "0x4d4f5e7a1fe57f5ceb38bfce8653effa5e584458": "MixOracle",
    "0x8de3ac42f800a1186b6d70cb91e0d6876cc36759": "ChainlinkOracle",
    "0x5f4ec3df9cbd43714fe2740f5e3616155c5b8419": "ChainlinkOracle 2",
    "0xa8f14f558ac70f5f52c37cd96d802ef9210023c5": "UniswapOracle",  # Outdated
    "0xc15169bad17e676b3badb699dee327423ce6178e": "UniswapOracle",
    "0x47211b1d1f6da45aaee06f877266e072cf8baa74": "CompoundStrategy",  # Outdated
    "0xfceea3923dd126d8fb3873389187307519c1de37": "CompoundStrategy Internal",  # Outdated
    "0x5b57e808b0ddcf097e25c5f5e3d8d3c2b0d26319": "CompoundStrategy Internal",  # Outdated
    "0xe40e09cd6725e542001fcb900d9dfea447b529c0": "3PoolStrategy USDT",
    "0x75bc09f72db1663ed35925b89de2b5212b9b6cb3": "3PoolStrategy USDT Internal",  # Outdated
    "0x641e3b5b081fb2fb8b43d5a163649312a28e23da": "3PoolStrategy USDT Internal",
    "0x67023c56548ba15ad3542e65493311f19adfdd6d": "3PoolStrategy USDC",
    "0x96e89b021e4d72b680bb0400ff504eb5f4a24327": "3PoolStrategy USDC Internal",
    "0xf92b0de25660c18bedaa55795986781d7899b0f9": "3PoolStrategy USDC Internal",  # Outdated
    "0x12115a32a19e4994c2ba4a5437c22cef5abb59c3": "CompoundStrategy DIA",
    "0xfaf23bd848126521064184282e8ad344490ba6f0": "CompoundStrategy DIA Internal",
    "0x051caefa90adf261b8e8200920c83778b7b176b6": "AaveStrategy",
    "0x5d9aa9f977e47ea0bfe61ba8b8f535aba02be135": "AaveStrategy Internal",
    "0x986b5e1e1755e3c2440e960477f25201b0a8bbd4": "Chainlink USDC ETH",
    "0x85ab3512465f39b8bb40a8872f8fbfd5f08ace1e": "Chainlink USDC ETH Internal",
    "0xde54467873c3bcaa76421061036053e371721708": "Chainlink USDC ETH Internal 2",
    "0x773616e4d11a78f511299002da57a0a94577f1f4": "Chainlink DAI ETH",
    "0x203030eeca9646f4ee21eb0f2358d8bfb7aa3881": "Chainlink DAI ETH Internal",
    "0x037e8f2125bf532f3e228991e051c8a7253b642c": "Chainlink DAI ETH Internal 2",
    "0xee9f2375b4bdf6387aa8265dd4fb8f16512a1d46": "Chainlink USDT ETH",
    "0x112cb637de6c1e6e71e8807ce9067aae5d5c192f": "Chainlink USDT ETH Internal",
    "0xa874fe207df445ff19e7482c746c4d3fd0cb9ace": "Chainlink USDT ETH Internal 2",
    "0x5f4ec3df9cbd43714fe2740f5e3616155c5b8419": "Chainlink Eth USD",
    "0xb103ede8acd6f0c106b7a5772e9d24e34f5ebc2c": "Chainlink Eth USD Internal",
    "0xf79d6afbb6da890132f9d7c355e3015f15f3406f": "Chainlink Eth USD Internal 2",
    "0x9b8eb8b3d6e2e0db36f41455185fef7049a35cae": "Open Price Feed",
    "0x922018674c12a7f0d394ebeef9b58f186cde13c1": "Open Price Feed 2",
    "0x197e90f9fad81970ba7976f33cbd77088e5d7cf7": "Mkr MCD Pot",
    "0x9759a6ac90977b93b58547b4a71c78317f391a28": "Mkr MCD Join DAI",
    "0x35d1b3f3d7966a1dfe207aa4514c12a259a0492b": "Mkr MCD Vat",
    "0xcc01d9d54d06b6a0b6d09a9f79c3a6438e505f71": "Uniswap V2: OUSD-USDT",
    "0x0d4a11d5eeaac28ec3f61d100daf4d40471f1852": "Uniswap V2: ETH-USDT",
    "0x7a250d5630b4cf539739df2c5dacb4c659f2488d": "Uniswap V2: Router",
    "0x0000000000000000000000000000000000000000": "The Void",
    "0xbebc44782c7db0a1a60cb6fe97d0b483032ff1c7": "Curve 3pool vault",
    "0x6c3f90f043a72fa612cbac8115ee7e52bde6e490": "Curve 3pool token",
    "0xbfcf63294ad7105dea65aa58f8ae5be2d9d0952a": "Curve 3pool gauge",
    "0xd533a949740bb3306d119cc777fa900ba034cd52": "Curve CRV token",
    "0x2f50d538606fa9edd2b11e2446beb18c9d5846bb": "Curve gauge controller",
    "0x5f3b5dfeb7b28cdbd7faba78963ee202a494e2a2": "Curve veCRV",
    "0xbfcf63294ad7105dea65aa58f8ae5be2d9d0952a": "Curve Token Minter",
    "0x111111125434b319222cdbf8c261674adb56f3ae": "1inch.exchange",
    "0x6ffe8f6d47afb19f12f46e5499a182a99c4d3bef": "Snowswap OUSD Lockup",
    "0x20d01749ccf2b689b758e07c597d9bb35370c378": "Mooniswap V1 (OUSD-USDT)",
    "0xd9e1ce17f2641f24ae83637ab66a2cca9c378b9f": "Sushiswap Router",
    "0xe4455fdec181561e9ffe909dde46aaeaedc55283": "Sushiswap OUSD-USDT",
}

SIGNATURES = {
    "0x07ea5477": "mintMultiple(address[],uint256[])",
    "0x23b872dd": "transferFrom(address,address,uint256)",
    "0xa9059cbb": "transfer(address,uint256)",
    "0x95d89b41": "symbol()",
    "0xfeaf968c": "latestRoundData()",
    "0x668a0f02": "latestRound()",
    "0xb5ab58dc": "getAnswer(uint256)",
    "0xb633620c": "getTimestamp(uint256)",
    "0x9478ab8c": "ethUsdPrice()",
    "0xfe2c6198": "price(string)",
    "0x313ce567": "decimals()",
    "0x18160ddd": "totalSupply()",
    "0x5f515226": "checkBalance(address)",
    "0x40c10f19": "mint(address,uint256)",
    "0x39a7919f": "changeSupply(uint256)",
    "0x70a08231": "balanceOf(address)",
    "0x182df0f5": "exchangeRateStored()",
    "0x0bebac86": "pie(address)",
    "0x19af6bf0": "priceMin(string)",
    "0x7bf0c215": "priceMax(string)",
    "0x2d9ff296": "tokEthPrice(string)",
    "0xaa388af6": "supportsAsset(address)",
    "0xc92aecc4": "chi()",
    "0x2f4350c2": "redeemAll()",
    "0x7ff36ab5": "swapExactETHForTokens(uint256,address[],address,uint256)",
    "0xbc25cf77": "skim(address)",
    "0x022c0d9f": "swap(uint256,uint256,address,bytes)",
    "0x0902f1ac": "getReserves()",
    "0x38ed1739": "swapExactTokensForTokens(uint256,uint256,address[],address,uint256)",
    "0x4515cef3": "add_liquidity(uint256[3],uint256)",
    "0xb6b55f25": "deposit(uint256)",
    "0x6a627842": "mint(address)",
    "0x2c4e722e": "rate()",
    "0xb26b238e": "future_epoch_time_write()",
    "0x615e5237": "checkpoint_gauge(address)",
    "0xd3078c945": "gauge_relative_weight(address,uint256)",
    "0x2e1a7d4d": "withdraw(uint256)",
    "0xabaa9916": "allocate()",
    "0x47e7ef24": "deposit(address,uint256)",
    "0xa0712d68": "mint(uint256)",
    "0x9f678cca": "drip()",
    "0xf24e23eb": "suck(address,address,uint256)",
    "0xfe0d94c1": "execute(uint256)",
    "0xc1a287e2": "GRACE_PERIOD()",
    "0xc9411e22": "addStrategy(address,uint256)",
    "0x4641257d": "harvest()",
    "0x0242241d": "collectRewardToken()",
    "0x125f9e33": "rewardTokenAddress()",
    "0x095ea7b3": "approve(address,uint256)",
    "0xeabe7d91": "redeemAllowed(address,address,uint256)",
    "0x51dff989": "redeemVerify(address,address,uint256,uint256)",
    "0xcc2b27d7": "calc_withdraw_one_coin(uint256,int128)",
    "0x5909c0d5": "price0CumulativeLast()",
    "0x5a3d5493": "price1CumulativeLast()",
    "0xfff6cae9": "sync()",
    "0x5d36b190": "claimGovernance()",
    "0x3659cfe6": "upgradeTo(address)",
    "0x372aa224": "setPriceProvider(address)",
    "0x8ec489a2": "setVaultBuffer(uint256)",
    "0x10d1e85c": "uniswapV2Call(address,uint256,uint256,bytes)",
}

EVENT_NAMES = {
    "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef": "Transfer(address,address,uint256)",
    "0x0f6798a560793a54c3bcfe86a93cde1e73087d944c0ea20544137d4121396885": "Mint(address,uint256)",
    "0x222838db2794d11532d940e8dec38ae307ed0b63cd97c233322e221f998767a6": "Redeem(address,uint256)",
    "0x99e56f783b536ffacf422d59183ea321dd80dcd6d23daa13023e8afea38c3df1": "TotalSupplyUpdated(uint256,uint256,uint256)",
    "0x9b15fe06f6132479e0c4d9dfbbff1de507a47663a459b2cc4ba1aa5a55e52058": "RewardTokenCollected(address,uint256)",
    "0x2ca0d37ecfc1b8853f4bc276c69586250b3978c1d467c05d6c143966026724ec": "SkippedWithdrawal(address,uint256)",
    "0xef6485b84315f9b1483beffa32aae9a0596890395e3d7521f1c5fbb51790e765": "PTokenAdded(address,address)",
    "0x5548c837ab068cf56a2c2479df0882a4922fd203edb7517321831d95078c5f62": "Deposit(address,address,uint256)",
    "0x2717ead6b9200dd235aad468c9809ea400fe33ac69b5bfaa6d3e90fc922b6398": "Withdrawal(address,address,uint256)",
    "0x79236a0cb516e4a8800fe3ac58e17c1eeb924b29658a461c9e65ed41d7db88f4": "Approval(address,address,uint)",
    "0x930a61a57a70a73c2a503615b87e2e54fe5b9cdeacda518270b852296ab1a377": "Transfer(address,address,uint)",
    "0x66c66224810ae56fadced079f9b31b994b686b0fab399bc95e32e55813d6d0b4": "Mint(address,amount0,amount1)",
    "0xd28e94e5f38ffc345d5364aefeee37a38ca95e1fb8101ca4a0c17abe86df9226": "Burn(address,amount0,amount1,address)",
    "0xd78ad95fa46c994b6551d0da85fc275fe613ce37657fb8d5e3d130840159d822": "Swap(address,uint256,uint256,uint256,uint256,address)",
    "0x1c411e9a96e071241c2f21f7726b17ae89e3cab4c78be50e062b03a9fffbbad1": "Sync(uint112,uint112)",
    "0x8c5be1e5ebec7d5bd14f71427d1e84f3dd0314c0f7b2291e5b200ac8c7c3b925": "Approval(address,address,uint256)",
    "0xa560e3198060a2f10670c1ec5b403077ea6ae93ca8de1c32b451dc1a943cd6e7": "ExecuteTransaction",
    "0x76e2796dc3a81d57b0e8504b647febcbeeb5f4af818e164f11eef8131a6a763f": "QueueTransaction",
}


@register.filter
@stringfilter
def hextoint(value):
    if value == None or value == "":
        return ""
    return int(value, 16)


@register.filter
@stringfilter
def contract_name(value):
    if value in CONTRACT_NAMES:
        return CONTRACT_NAMES[value]
    else:
        return value


@register.filter
@stringfilter
def method_name(value):
    value = value[0:10]
    if value in SIGNATURES:
        return SIGNATURES[value]
    else:
        return value


@register.filter
@stringfilter
def event_name(value):
    if value in EVENT_NAMES:
        return EVENT_NAMES[value]
    else:
        return value


@register.filter
@stringfilter
def long_address_name(value):
    address = "0x" + value[-40:]
    return contract_name(address)


@register.filter
def decode_execute_event_signature(value):
    abi = "(uint256,string,bytes,uint256)"
    b = bytearray.fromhex(value[2:])  # bytearray hates the 0x
    return decode_single(abi, b)[1]


@register.filter
def dec_18(value):
    if isinstance(value, str):
        return int(value, 16) / 1e18


@register.filter
def dec_6(value):
    if isinstance(value, str):
        return int(value, 16) / 1e6


@register.filter
def slot_0(value):
    return _slot(value, 0)


@register.filter
def slot_1(value):
    return _slot(value, 1)


@register.filter
def slot_2(value):
    return _slot(value, 2)


@register.filter
def slot_3(value):
    return _slot(value, 3)


@register.filter
def explode_data(value):
    count = len(value) // 64
    out = []
    for i in range(0, count):
        out.append(dec_18(value[2 + i * 64 : 2 + i * 64 + 64]))
    return out


def _snarf_input_symbol(trace):
    s = trace["action"]["input"][64 + 10 + 64 :]
    out = unhexlify(s).decode("utf-8")
    return out


@register.filter
def local_time(dt):
    utc = dt.replace(tzinfo=pytz.UTC)
    localtz = utc.astimezone(timezone.get_current_timezone())
    return "{d:%l}:{d.minute:02}{d:%p} {d:%b} {d.day}, {d.year} {d:%Z}".format(
        d=localtz
    )


@register.filter
def sub(v, arg):
    return v - arg


@register.filter
def trace_annotation(trace):
    # mixOracle, priceMin
    to = trace["action"]["to"]
    signature = trace["action"]["input"][0:10]
    # print(to, signature)
    if not "result" in trace:
        return "❌"
    if to == "0xcf67e56965ad7cec05ebf88bad798a875e0460eb" and signature == "0x19af6bf0":
        symbol = _snarf_input_symbol(trace)
        value = Decimal(int(trace["result"]["output"], 16)) / Decimal(1e8)
        return "🏛 %s at $%s" % (symbol, value)
    elif (
        to == "0x9b8eb8b3d6e2e0db36f41455185fef7049a35cae"
        or to == "0x922018674c12a7f0d394ebeef9b58f186cde13c1"
    ) and signature == "0xfe2c6198":
        symbol = _snarf_input_symbol(trace)
        value = Decimal(int(trace["result"]["output"], 16)) / Decimal(1e6)
        return "🏛🏛 %s at $%s" % (symbol, value)
    elif (
        to == "0x5f4ec3df9cbd43714fe2740f5e3616155c5b8419" and signature == "0xfeaf968c"
    ):
        s = "0x" + trace["result"]["output"][2 + 64 : 2 + 64 + 64]
        value = Decimal(int(s, 16)) / Decimal(1e8)
        return "🏛🏛 CHAIN ETH %f" % value
    elif signature == "0xfeaf968c":
        s = "0x" + trace["result"]["output"][2 + 64 : 2 + 64 + 64]
        print(s)
        value = Decimal(int(s, 16)) / Decimal(1e8)
        return "CHAIN %f" % value

    return "."
