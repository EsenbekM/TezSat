# Generated by Django 3.1.3 on 2021-07-14 19:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0030_auto_20210705_1359'),
    ]

    operations = [
        migrations.AddField(
            model_name='productreview',
            name='is_read',
            field=models.BooleanField(default=False),
        ),
    ]
