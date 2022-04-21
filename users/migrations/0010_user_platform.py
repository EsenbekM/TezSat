# Generated by Django 3.0.6 on 2020-05-16 14:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0009_auto_20200502_0057'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='platform',
            field=models.CharField(blank=True, choices=[('ios', 'ios'), ('android', 'android')], max_length=20, null=True, verbose_name='platform'),
        ),
    ]