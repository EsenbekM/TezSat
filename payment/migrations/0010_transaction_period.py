# Generated by Django 3.1.3 on 2021-08-27 04:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0009_auto_20210826_1527'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='period',
            field=models.IntegerField(blank=True, null=True, verbose_name='period'),
        ),
    ]
