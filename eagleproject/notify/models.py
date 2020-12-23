from django.db import models


class CursorId(models.TextChoices):
    TRANSACTIONS = 'tx', 'Transactions'
    TRANSFERS = 'tr', 'Transfers'
    SNAPSHOT = 'sn', 'Snapshots'


class NotifyCursor(models.Model):
    cursor_id = models.CharField(
        max_length=2,
        choices=CursorId.choices,
        primary_key=True
    )
    block_number = models.IntegerField()
    last_update = models.DateTimeField()

    class Meta:
        indexes = [
            models.Index(fields=["cursor_id", "block_number"]),
        ]
