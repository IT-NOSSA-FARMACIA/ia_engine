# Generated by Django 3.2.5 on 2022-01-10 22:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api_engine', '0013_functionserviceexecution'),
    ]

    operations = [
        migrations.AddField(
            model_name='functionserviceexecution',
            name='status_code',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]