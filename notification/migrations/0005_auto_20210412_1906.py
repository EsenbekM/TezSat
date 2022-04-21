# Generated by Django 3.1.3 on 2021-04-12 13:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notification', '0004_pushnotification'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='action',
            field=models.CharField(choices=[('activated', 'activated'), ('stared', 'stared'), ('blocked', 'blocked')], max_length=50, verbose_name='action'),
        ),
    ]