from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0021_create_etherscan_pointer"),
    ]

    operations = [
        migrations.CreateModel(
            name="OgnStaked",
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
                ("user_address", models.CharField(db_index=True, max_length=42)),
                ("is_staked", models.BooleanField()),
                (
                    "amount",
                    models.DecimalField(decimal_places=18, default=0, max_digits=64),
                ),
            ],
        ),
    ]
