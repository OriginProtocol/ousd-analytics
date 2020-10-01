from django.shortcuts import render
from django.db.models import Q
from core.blockchain import (
    build_asset_block,
    build_debug_tx,
    lastest_block,
    ensure_latest_logs,
    download_logs_from_contract,
    totalSupply,
)
from core.models import AssetBlock, DebugTx, LogPointer, Log

import core.blockchain as blockchain


def dashboard(request):
    # AssetBlock.objects.all().delete()
    block_number = lastest_block() - 2

    dai = ensure_asset("DAI", block_number)
    usdt = ensure_asset("USDT", block_number)
    usdc = ensure_asset("USDC", block_number)

    assets = [dai, usdt, usdc]
    total_vault = sum(x.vault_holding * x.ora_tok_usd_min for x in assets)
    total_compstrat = sum(x.compstrat_holding * x.ora_tok_usd_min for x in assets)
    total_assets = total_vault + total_compstrat
    total_supply = totalSupply(blockchain.OUSD, 18, block_number)

    ensure_latest_logs(block_number)

    logs_q = Log.objects.all()
    if request.GET.get("topic_0"):
        logs_q = logs_q.filter(topic_0=request.GET.get("topic_0"))
    latest_logs = logs_q[:100]

    return render(request, "dashboard.html", locals())


def address(request, address):
    block_number = lastest_block() - 2
    if request.GET.get("blocks"):
        blocks = int(request.GET.get("blocks"))
    else:
        blocks = 200
    past_block_number = block_number - blocks

    now = _my_assets(address, block_number)
    before = _my_assets(address, past_block_number)
    return render(request, "address.html", locals())


def _my_assets(address, block_number):
    dai = ensure_asset("DAI", block_number)
    usdt = ensure_asset("USDT", block_number)
    usdc = ensure_asset("USDC", block_number)
    total_supply = totalSupply(blockchain.OUSD, 18, block_number)

    current_balance = blockchain.balanceOf(blockchain.OUSD, address, 18, block_number)
    total_supply = totalSupply(blockchain.OUSD, 18, block_number)
    print(block_number, current_balance, total_supply)

    return {
        "my": {
            "DAI": (dai.vault_holding + dai.compstrat_holding)
            * current_balance
            / total_supply,
            "USDC": (usdc.vault_holding + usdc.compstrat_holding)
            * current_balance
            / total_supply,
            "USDT": (usdt.vault_holding + usdt.compstrat_holding)
            * current_balance
            / total_supply,
        },
        "current_balance": current_balance,
        "total_supply": total_supply,
    }


def tx_debug(request, tx_hash):
    debug_tx = ensure_debug_tx(tx_hash)
    return render(request, "debug_tx.html", locals())


def address_balance(request, address):
    current_balance = blockchain.balanceOf(blockchain.OUSD, address, 18)
    long_address = address.replace("0x", "0x000000000000000000000000")
    TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
    SUPPLY = "0x99e56f783b536ffacf422d59183ea321dd80dcd6d23daa13023e8afea38c3df1"

    transfer_logs = list(
        Log.objects.filter(address=blockchain.OUSD, topic_0=TRANSFER).filter(
            Q(topic_1=long_address) | Q(topic_2=long_address)
        )
    )
    supply_logs = list(Log.objects.filter(address=blockchain.OUSD, topic_0=SUPPLY))
    all_logs = transfer_logs + supply_logs
    all_logs = sorted(
        all_logs, key=lambda x: (x.block_number, x.log_index), reverse=True
    )

    for log in all_logs:
        log.account_balance = blockchain.balanceOf(
            blockchain.OUSD, address, 18, log.block_number
        )

    # balance = current_balance
    # balances = []
    # logs_len = len(all_logs)
    # supply_i = -1
    # transfer_i = 0
    # ratio = 0
    # while transfer_i < logs_len:
    #     if all_logs[transfer_i].topic_0 == TRANSFER:
    #         amount = int(all_logs[transfer_i].data, 16)
    #         if all_logs[transfer_i].topic_1 == long_address:
    #             amount = amount * -1
    #         while supply_i < transfer_i:
    #             supply_i += 1
    #             if all_logs[supply_i].topic_0 == SUPPLY:
    #                 rate = int(all_logs[supply_i].data[2 + 64 * 2 :], 16)
    #                 print("FOUND", rate)
    #             if supply_i >= logs_len:
    #                 break

    #         print(
    #             "XFER",
    #             amount,
    #         )
    #     transfer_i += 1

    return render(request, "address_balance.html", locals())


def ensure_asset(symbol, block_number):
    q = AssetBlock.objects.filter(symbol=symbol, block_number=block_number)
    if q.count():
        return q.first()
    else:
        ab = build_asset_block(symbol, block_number)
        ab.save()
        return ab


def ensure_debug_tx(tx_hash):
    if DebugTx.objects.filter(tx_hash=tx_hash).count() == 0:
        ab = build_debug_tx(tx_hash)
        ab.save()
    else:
        ab = DebugTx.objects.filter(tx_hash=tx_hash).first()
    return ab