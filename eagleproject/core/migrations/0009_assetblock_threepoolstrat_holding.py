# Generated by Django 3.1.1 on 2020-10-16 11:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0008_supplysnapshot"),
    ]

    operations = [
        migrations.AddField(
            model_name="assetblock",
            name="threepoolstrat_holding",
            field=models.DecimalField(decimal_places=18, default=0, max_digits=64),
        ),
    ]
