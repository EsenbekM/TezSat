# Generated by Django 3.1.3 on 2021-11-02 11:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0010_transaction_period'),
    ]

    operations = [
        migrations.RenameField(
            model_name='tariff',
            old_name='name_kgz',
            new_name='title_ky',
        ),
        migrations.RenameField(
            model_name='tariff',
            old_name='name_ru',
            new_name='title_ru',
        ),
    ]
