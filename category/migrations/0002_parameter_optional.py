# Generated by Django 3.0.5 on 2020-04-14 16:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('category', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='parameter',
            name='optional',
            field=models.BooleanField(default=True, verbose_name='optional'),
        ),
    ]
