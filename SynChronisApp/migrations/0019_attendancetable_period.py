# Generated by Django 4.2.19 on 2025-02-15 09:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SynChronisApp', '0018_remove_studentnoticetable_batchname_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='attendancetable',
            name='Period',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
