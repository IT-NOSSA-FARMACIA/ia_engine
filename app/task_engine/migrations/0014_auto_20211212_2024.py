# Generated by Django 3.2.5 on 2021-12-12 20:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('task_engine', '0013_alter_ticketparameter_value'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalschedule',
            name='emails_to_notification',
            field=models.CharField(blank=True, max_length=2000, null=True),
        ),
        migrations.AddField(
            model_name='historicalschedule',
            name='notification_type',
            field=models.CharField(choices=[('NE', 'Nunca'), ('ER', 'Apenas Erro'), ('SC', 'Apenas Sucesso'), ('AL', 'Sempre')], default='NE', max_length=2),
        ),
        migrations.AddField(
            model_name='schedule',
            name='emails_to_notification',
            field=models.CharField(blank=True, max_length=2000, null=True),
        ),
        migrations.AddField(
            model_name='schedule',
            name='notification_type',
            field=models.CharField(choices=[('NE', 'Nunca'), ('ER', 'Apenas Erro'), ('SC', 'Apenas Sucesso'), ('AL', 'Sempre')], default='NE', max_length=2),
        ),
    ]
