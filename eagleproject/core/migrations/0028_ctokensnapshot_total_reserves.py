# Generated by Django 3.1.1 on 2021-01-19 17:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0027_ognstaked_stake_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='ctokensnapshot',
            name='total_reserves',
            field=models.DecimalField(decimal_places=18, default=0, max_digits=64),
            preserve_default=False,
        ),
    ]
