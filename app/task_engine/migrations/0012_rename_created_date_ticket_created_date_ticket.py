# Generated by Django 3.2.5 on 2021-09-23 20:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('task_engine', '0011_create_viewer_permission'),
    ]

    operations = [
        migrations.RenameField(
            model_name='ticket',
            old_name='created_date',
            new_name='created_date_ticket',
        ),
    ]