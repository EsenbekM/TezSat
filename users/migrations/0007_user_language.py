# Generated by Django 3.0.5 on 2020-04-14 10:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_auto_20200411_1339'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='language',
            field=models.CharField(blank=True, choices=[('ru', 'ru'), ('ky', 'ky')], default='ky', max_length=10, null=True, verbose_name='language'),
        ),
    ]