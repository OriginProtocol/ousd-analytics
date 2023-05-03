# Generated by Django 4.1.7 on 2023-05-02 10:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("notify", "0006_update_notifycursor_index"),
    ]

    operations = [
        migrations.AlterField(
            model_name="notifycursor",
            name="cursor_id",
            field=models.CharField(
                choices=[
                    ("tx", "Transactions"),
                    ("tr", "Transfers"),
                    ("sn", "Snapshots"),
                    ("oeth_tx", "OETH Transactions"),
                    ("oeth_tr", "OETH Transfers"),
                    ("oeth_sn", "OETH Snapshots"),
                ],
                max_length=8,
                primary_key=True,
                serialize=False,
            ),
        ),
    ]
