# Generated by Django 3.2.5 on 2022-06-26 23:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('task_engine', '0016_historicalteamworker_teamworker'),
    ]

    operations = [
        migrations.AddField(
            model_name='ticket',
            name='external_id',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='scheduleexecution',
            name='execution_status',
            field=models.CharField(choices=[('PE', 'Pending'), ('PR', 'Processing'), ('SC', 'Success'), ('ER', 'Error'), ('QU', 'Queue'), ('RT', 'Queue (Retry)'), ('CT', 'Creating tickets')], default='PE', max_length=2),
        ),
        migrations.AlterField(
            model_name='ticket',
            name='execution_status',
            field=models.CharField(choices=[('PE', 'Pending'), ('PR', 'Processing'), ('SC', 'Success'), ('ER', 'Error'), ('QU', 'Queue'), ('RT', 'Queue (Retry)'), ('CT', 'Creating tickets')], default='PE', max_length=2),
        ),
    ]
