# Generated by Django 3.2.8 on 2021-11-09 08:55

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0041_auto_20211108_1351'),
    ]

    operations = [
        migrations.AddField(
            model_name='analyticsreport',
            name='accounts_holding_more_than_100_ousd_after_curve_start',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='analyticsreport',
            name='new_accounts_after_curve_start',
            field=models.IntegerField(default=0),
        ),
    ]
