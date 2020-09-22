from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

CONTRACT_NAMES = {
    "0x277e80f3e14e7fb3fc40a9d6184088e0241034bd": "Vault",
    "0x2a8e1e676ec238d8a992307b495b45b3feaa5e86": "OUSD",
    "0x3c09b440f9e46c0e4a665539aeca80fcaa92c36e": "OUSD Internal",
    "0xa7f26e9aeeea4fe16d9c4a6a0464af8258f437bb": "Vault Internal",
    "0xf251cb9129fdb7e9ca5cad097de3ea70cab9d8f9": "Vault Internal",
    "0xdac17f958d2ee523a2206206994597c13d831ec7": "USDT",
    "0x6b175474e89094c44da98b954eedeac495271d0f": "DAI",
    "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48": "USDC",
    "0xb7277a6e95992041568d9391d09d0122023778a2": "USDC Internal",
    "0x5d3a536e4d6dbd6114cc1ead35777bab948e3643": "cDAI",
    "0xbb8be4772faa655c255309afc3c5207aa7b896fd": "cDAI Storage",
    "0x39aa39c021dfbae8fac545936693ac917d5e7563": "cUSDC",
    "0xf650c3d88d12db855b8bf7d11be6c55a4e07dcc9": "cUSDT",
    "0x976aa93ca5aaa569109f4267589c619a097f001d": "cUSDT Internal",
    "0xcf67e56965ad7cec05ebf88bad798a875e0460eb": "MixOracle",
    "0x8de3ac42f800a1186b6d70cb91e0d6876cc36759": "ChainlinkOracle",
    "0x5f4ec3df9cbd43714fe2740f5e3616155c5b8419": "ChainlinkOracle 2",
    "0xa8f14f558ac70f5f52c37cd96d802ef9210023c5": "UniswapOracle",
    "0x47211b1d1f6da45aaee06f877266e072cf8baa74": "CompoundStrategy",
    "0xfceea3923dd126d8fb3873389187307519c1de37": "CompoundStrategy Internal",
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
    "0x197e90f9fad81970ba7976f33cbd77088e5d7cf7": "Mkr MCD  Pot",
    "0xcc01d9d54d06b6a0b6d09a9f79c3a6438e505f71": "OUSD/USDT Uniswap",
    "0x0000000000000000000000000000000000000000": "The Void",
}

SIGNATURES = {
    "0x07ea5477": "mintMultiple(address[],uint256[])",
    "0x23b872dd": "transferFrom(address,address,uint256)",
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
    "": "",
    "": "",
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
    "0x": "",
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
    address = "0x"+value[-40:]
    return contract_name(address)

    

@register.filter
def dec_18(value):
    if isinstance(value, str):
        return int(value, 16) / 1e18
