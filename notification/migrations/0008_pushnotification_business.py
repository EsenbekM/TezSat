# Generated by Django 3.1.3 on 2021-08-11 07:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notification', '0007_pushnotification_minutes'),
    ]

    operations = [
        migrations.AddField(
            model_name='pushnotification',
            name='business',
            field=models.BooleanField(default=False, verbose_name='business push or not'),
        ),
    ]
