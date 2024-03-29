# Generated by Django 3.2.8 on 2021-11-08 13:51

import datetime
from django.db import migrations, models

def populate_(apps, schema_editor):
    if schema_editor.connection.vendor.startswith('postgres'):
        schema_editor.execute(
            "UPDATE core_analyticsreport SET report='[]';"
        )
    else:
        # TODO:
        # should also provide a sqlLite implementation
        raise Exception('This migration is not implemented in sqlLite. Bug domeng to do it')


    if schema_editor.connection.vendor.startswith('postgres'):
        schema_editor.execute(
            "UPDATE core_transaction SET from_address=receipt_data->>'from';"
        )
    else:
        # TODO:
        # should also provide a sqlLite implementation
        raise Exception('This migration is not implemented in sqlLite. Bug domeng to do it')


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0040_auto_20211021_1308'),
    ]

    operations = [
        migrations.AddField(
            model_name='analyticsreport',
            name='report',
            field=models.JSONField(default=list),
        ),
        migrations.AddField(
            model_name='transaction',
            name='from_address',
            field=models.CharField(db_index=True, default='0xinvalid_address', max_length=42),
        ),
        migrations.RunPython(populate_),
    ]
