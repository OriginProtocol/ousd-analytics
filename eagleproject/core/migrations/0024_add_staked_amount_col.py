from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0023_create_ogn_staking_snapshot'),
    ]

    operations = [
        migrations.AddField(
            model_name='OgnStaked',
            name='staked_amount',
            field=models.DecimalField(decimal_places=18, default=0, max_digits=64),
        ),
    ]
