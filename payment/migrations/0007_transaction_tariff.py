# Generated by Django 3.1.3 on 2021-08-11 05:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0006_auto_20210809_1306'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='tariff',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='tariff', to='payment.tariff'),
        ),
    ]
