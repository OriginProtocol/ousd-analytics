# Generated by Django 3.1.1 on 2021-01-26 17:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0030_ctokensnapshot_total_cash'),
    ]

    operations = [
        migrations.AddField(
            model_name='log',
            name='topic_3',
            field=models.CharField(blank=True, db_index=True, max_length=255),
        ),
    ]