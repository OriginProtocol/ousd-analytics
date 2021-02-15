# Generated by Django 3.1.1 on 2021-02-15 19:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0035_threepoolsnapshot'),
    ]

    operations = [
        migrations.RunSQL(
            "DELETE FROM core_log cl1 "
            "WHERE cl1.id = ("
            "    SELECT MAX(scl1.id)"
            "    FROM core_log scl1"
            "    LEFT JOIN core_log scl2 ON ("
            "        scl1.block_number = scl2.block_number "
            "        AND scl1.transaction_index = scl2.transaction_index "
            "        AND scl1.log_index = scl2.log_index "
            "        AND scl1.id != scl2.id"
            "    )"
            "    WHERE scl2.id IS NOT NULL"
            "    AND cl1.block_number = scl1.block_number "
            "    AND cl1.transaction_index = scl1.transaction_index "
            "    AND cl1.log_index = scl1.log_index "
            ");",
        ),
        migrations.AlterUniqueTogether(
            name='log',
            unique_together={('block_number', 'transaction_index', 'log_index')},
        ),
    ]
