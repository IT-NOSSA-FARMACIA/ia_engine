# Generated by Django 3.2.5 on 2022-04-28 19:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('task_engine', '0014_auto_20211212_2024'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ticketparameter',
            name='value',
            field=models.TextField(blank=True, null=True),
        ),
    ]
