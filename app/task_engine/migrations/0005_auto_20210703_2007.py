# Generated by Django 3.2.4 on 2021-07-03 20:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('task_engine', '0004_auto_20210702_2351'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='schedule',
            name='full_date',
        ),
        migrations.AddField(
            model_name='schedule',
            name='cron',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]
