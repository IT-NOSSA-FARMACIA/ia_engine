# Generated by Django 3.2.5 on 2021-07-30 16:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api_engine', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='domainfunctionservice',
            name='active',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='functionservice',
            name='active',
            field=models.BooleanField(default=True),
        ),
    ]
