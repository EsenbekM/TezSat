# Generated by Django 3.1.3 on 2021-09-24 08:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notification', '0011_auto_20210914_1229'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='description_ky',
            field=models.CharField(blank=True, max_length=500, null=True, verbose_name='description'),
        ),
        migrations.AlterField(
            model_name='notification',
            name='description_ru',
            field=models.CharField(blank=True, max_length=500, null=True, verbose_name='description'),
        ),
    ]
