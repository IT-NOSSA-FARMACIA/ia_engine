# Generated by Django 3.2.4 on 2021-07-03 23:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('task_engine', '0010_stepschedule_stoppable'),
    ]

    operations = [
        migrations.AddField(
            model_name='action',
            name='active',
            field=models.BooleanField(default=True),
        ),
    ]
