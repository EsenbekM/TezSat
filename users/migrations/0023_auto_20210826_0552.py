# Generated by Django 3.1.3 on 2021-08-25 23:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0022_merge_20210826_0549'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='remove_layout',
            field=models.DateField(blank=True, null=True, verbose_name='remove layout'),
        ),
        migrations.AlterField(
            model_name='user',
            name='request_status',
            field=models.CharField(choices=[('not_requested', 'not_requested'), ('accepted', 'accepted'), ('success', 'success'), ('on_review', 'on_review'), ('expired', 'expired'), ('not_request_none', 'not_request_none'), ('expired_none', 'expired_none')], default='not_requested', max_length=50, verbose_name='business request status'),
        ),
    ]
