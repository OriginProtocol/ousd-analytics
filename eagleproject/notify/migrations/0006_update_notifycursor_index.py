# Generated by Django 4.1.7 on 2023-05-01 14:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("notify", "0005_notifycursor_project"),
    ]

    operations = [
        migrations.RemoveIndex(
            model_name="notifycursor",
            name="notify_noti_cursor__c9a9e0_idx",
        ),
        migrations.AddIndex(
            model_name="notifycursor",
            index=models.Index(
                fields=["cursor_id", "block_number", "project"],
                name="notify_noti_cursor__9f7566_idx",
            ),
        ),
    ]
