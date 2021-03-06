# Generated by Django 3.1.3 on 2021-09-01 05:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0023_auto_20210826_0552'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='request_status',
            field=models.CharField(choices=[('not_requested', 'not_requested'), ('accepted', 'accepted'), ('success', 'success'), ('on_review', 'on_review'), ('expired', 'expired'), ('not_request_none', 'not_request_none'), ('expired_none', 'expired_none'), ('normal', 'normal')], default='not_requested', max_length=50, verbose_name='business request status'),
        ),
    ]
