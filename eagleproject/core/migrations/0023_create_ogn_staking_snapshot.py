# Generated by Django 3.1.1 on 2020-12-22 19:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0022_ognstaked'),
    ]

    operations = [
        migrations.CreateModel(
            name='OgnStakingSnapshot',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('block_number', models.IntegerField(db_index=True)),
                ('ogn_balance', models.DecimalField(decimal_places=18, max_digits=64)),
                ('total_outstanding', models.DecimalField(decimal_places=18, max_digits=64)),
            ],
        ),
    ]