# Generated by Django 4.2.19 on 2025-02-16 09:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SynChronisApp', '0019_attendancetable_period'),
    ]

    operations = [
        migrations.AddField(
            model_name='subjectstable',
            name='SubjectType',
            field=models.CharField(blank=True, choices=[('Theory', 'Theory'), ('Practical', 'Practical')], max_length=50, null=True),
        ),
    ]
