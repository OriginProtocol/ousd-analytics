# Generated by Django 3.1.1 on 2020-11-13 15:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0017_delete_ousdtransfer"),
    ]

    operations = [
        migrations.CreateModel(
            name="OusdTransfer",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("tx_hash", models.CharField(db_index=True, max_length=66)),
                ("log_index", models.CharField(db_index=True, max_length=66)),
                ("block_time", models.DateTimeField(db_index=True)),
                ("from_address", models.CharField(db_index=True, max_length=42)),
                ("to_address", models.CharField(db_index=True, max_length=42)),
                (
                    "amount",
                    models.DecimalField(decimal_places=18, default=0, max_digits=64),
                ),
            ],
        ),
    ]
