from django.db import models

from core.models import OriginTokens


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

    project = models.TextField(
        choices=OriginTokens.choices,
        default=OriginTokens.OUSD
    )

    class Meta:
        indexes = [
            models.Index(fields=["cursor_id", "block_number"]),
        ]


class EventSeen(models.Model):
    event_hash = models.CharField(max_length=64, primary_key=True)
    last_seen = models.DateTimeField()

    class Meta:
        indexes = [models.Index(fields=["last_seen"])]
