from django.db import models
from decimal import Decimal


class AssetBlock(models.Model):
    symbol = models.CharField(max_length=8, db_index=True)
    block_number = models.IntegerField(db_index=True)
    ora_tok_usd_min = models.DecimalField(max_digits=64, decimal_places=18, default=0)
    ora_tok_usd_max = models.DecimalField(max_digits=64, decimal_places=18, default=0)
    vault_holding = models.DecimalField(max_digits=64, decimal_places=18, default=0)
    compstrat_holding = models.DecimalField(max_digits=64, decimal_places=18, default=0)
    threepoolstrat_holding = models.DecimalField(
        max_digits=64, decimal_places=18, default=0
    )
    aavestrat_holding = models.DecimalField(max_digits=64, decimal_places=18, default=0)

    def ora_diff_basis(self):
        return (self.ora_tok_usd_max - self.ora_tok_usd_min) * Decimal(10000)

    def total(self):
        return (
            self.vault_holding
            + self.compstrat_holding
            + self.threepoolstrat_holding
            + self.aavestrat_holding
        )

    def redeem_value(self):
        return self.total() * self.redeem_price()

    def redeem_price(self):
        if self.ora_tok_usd_max > 1.0:
            return self.ora_tok_usd_max
        else:
            return Decimal(1)

    class Meta:
        indexes = [
            models.Index(fields=["block_number"]),
        ]


class DebugTx(models.Model):
    tx_hash = models.CharField(max_length=66, db_index=True)
    block_number = models.IntegerField(db_index=True)
    notes = models.TextField()
    data = models.JSONField()


class LogPointer(models.Model):
    contract = models.CharField(max_length=256, db_index=True)
    last_block = models.IntegerField(db_index=True)


class Log(models.Model):
    address = models.CharField(max_length=255, db_index=True)
    event_name = models.CharField(max_length=255, db_index=True, blank=True)
    topic_0 = models.CharField(max_length=255, db_index=True, blank=True)
    topic_1 = models.CharField(max_length=255, db_index=True, blank=True)
    topic_2 = models.CharField(max_length=255, db_index=True, blank=True)
    data = models.TextField(max_length=256, blank=True)
    block_number = models.IntegerField(db_index=True)
    log_index = models.IntegerField(db_index=True)
    transaction_hash = models.CharField(max_length=255, db_index=True)
    transaction_index = models.IntegerField(db_index=True)
    account_balance = Decimal(0)

    def is_ousd_in(self):
        """For uniswap events"""
        return (
            self.data[2 + 3 * 64 : 2 + 4 * 64]
            != "0000000000000000000000000000000000000000000000000000000000000000"
        )

    class Meta:
        ordering = ["-block_number", "-log_index"]
        indexes = [
            models.Index(fields=["block_number"]),
        ]


class SupplySnapshot(models.Model):
    block_number = models.IntegerField(db_index=True)
    reported_supply = models.DecimalField(max_digits=64, decimal_places=18)
    computed_supply = models.DecimalField(max_digits=64, decimal_places=18)
    non_rebasing_credits = models.DecimalField(
        max_digits=64, decimal_places=18, default=0
    )
    non_rebasing_supply = models.DecimalField(
        max_digits=64, decimal_places=18, default=0
    )
    credits = models.DecimalField(max_digits=64, decimal_places=18)
    credits_ratio = models.DecimalField(max_digits=64, decimal_places=18)
    rebasing_credits_ratio = models.DecimalField(
        max_digits=64, decimal_places=18, default=0
    )
    apr = Decimal(0)  # Not persisted
    gain = Decimal(0)  # Not persisted

    def backing_diff(self):
        return self.computed_supply - self.reported_supply

    def non_rebasing_percentage(self):
        return (self.non_rebasing_supply / self.computed_supply) * 100

    def non_rebasing_boost_percentage(self):
        return (
            (self.computed_supply / (self.computed_supply - self.non_rebasing_supply))
            - 1
        ) * 100

    class Meta:
        ordering = ["-block_number"]
        indexes = [
            models.Index(fields=["block_number"]),
        ]
