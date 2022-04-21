# Generated by Django 3.1.3 on 2021-08-07 20:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0018_user_request_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='balance',
            field=models.IntegerField(default=0, verbose_name='Balance'),
        ),
        migrations.AlterField(
            model_name='user',
            name='request_status',
            field=models.CharField(choices=[('not_requested', 'not_requested'), ('accepted', 'accepted'), ('success', 'success'), ('on_review', 'on_review')], default='not_requested', max_length=50, verbose_name='business request status'),
        ),
    ]