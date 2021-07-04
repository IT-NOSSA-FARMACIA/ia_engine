# Generated by Django 3.2.4 on 2021-07-02 23:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('task_engine', '0003_schedule_cron_schedule'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='schedule',
            name='cron_schedule',
        ),
        migrations.AddField(
            model_name='schedule',
            name='active',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='schedule',
            name='days',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
        migrations.AddField(
            model_name='schedule',
            name='full_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='schedule',
            name='hours',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
        migrations.AddField(
            model_name='schedule',
            name='last_execution',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='schedule',
            name='last_value',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='schedule',
            name='minutes',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
    ]
