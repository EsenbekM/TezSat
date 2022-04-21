# Generated by Django 3.1.3 on 2021-08-11 07:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0007_transaction_tariff'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tariff',
            name='name',
        ),
        migrations.AddField(
            model_name='tariff',
            name='name_kgz',
            field=models.CharField(max_length=50, null=True, verbose_name='kgz'),
        ),
        migrations.AddField(
            model_name='tariff',
            name='name_ru',
            field=models.CharField(max_length=50, null=True, verbose_name='ru'),
        ),
    ]