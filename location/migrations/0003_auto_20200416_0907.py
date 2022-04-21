# Generated by Django 3.0.5 on 2020-04-16 09:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('location', '0002_auto_20200415_0903'),
    ]

    operations = [
        migrations.AddField(
            model_name='location',
            name='request_ky',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='request in kyrgyz'),
        ),
        migrations.AddField(
            model_name='location',
            name='request_ru',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='request in russian'),
        ),
    ]
