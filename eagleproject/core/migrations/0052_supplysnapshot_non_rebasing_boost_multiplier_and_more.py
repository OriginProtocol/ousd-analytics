# Generated by Django 4.1.7 on 2023-08-15 19:06

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0051_update_analytics_reports"),
    ]

    operations = [
        migrations.AddField(
            model_name="supplysnapshot",
            name="non_rebasing_boost_multiplier",
            field=models.DecimalField(decimal_places=18, default=0, max_digits=64),
        ),
    ]
