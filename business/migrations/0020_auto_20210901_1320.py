# Generated by Django 3.1.3 on 2021-09-01 07:20

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('business', '0019_business_delivery'),
    ]

    operations = [
        migrations.AddField(
            model_name='business',
            name='deactivate_date',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2021, 11, 1, 0, 0), verbose_name='Дата деактивации'),
        ),
        migrations.AlterField(
            model_name='businessschedule',
            name='weekday',
            field=models.CharField(choices=[('monday', 'пн'), ('tuesday', 'вт'), ('wednesday', 'ср'), ('thursday', 'чт'), ('friday', 'пт'), ('saturday', 'сб'), ('sunday', 'вс')], max_length=100, verbose_name='weekday'),
        ),
    ]
