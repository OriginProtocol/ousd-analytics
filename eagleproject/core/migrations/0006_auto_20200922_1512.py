# Generated by Django 3.1.1 on 2020-09-22 15:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0005_log"),
    ]

    operations = [
        migrations.RenameField(
            model_name="log",
            old_name="transactionIndex",
            new_name="transaction_index",
        ),
    ]
