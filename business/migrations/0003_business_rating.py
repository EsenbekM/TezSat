# Generated by Django 3.0.6 on 2020-07-09 11:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('business', '0002_auto_20200709_1401'),
    ]

    operations = [
        migrations.AddField(
            model_name='business',
            name='rating',
            field=models.SmallIntegerField(null=True, verbose_name='rating'),
        ),
    ]
