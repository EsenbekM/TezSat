# Generated by Django 3.0.5 on 2020-04-22 07:31

from django.db import migrations
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0006_auto_20200420_0922'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productcontact',
            name='phone',
            field=phonenumber_field.modelfields.PhoneNumberField(max_length=128, region=None, verbose_name='phone number'),
        ),
    ]
