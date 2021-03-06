# Generated by Django 3.0.6 on 2020-07-16 07:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('business', '0006_business_upvote_count'),
    ]

    operations = [
        migrations.AlterField(
            model_name='business',
            name='upvote_count',
            field=models.SmallIntegerField(default=2, verbose_name='auto upvote count'),
        ),
        migrations.AlterField(
            model_name='businesscontact',
            name='type',
            field=models.CharField(choices=[('phone', 'phone'), ('email', 'email'), ('website', 'website'), ('facebook', 'facebook'), ('instagram', 'instagram'), ('whatsapp', 'whatsapp'), ('telegram', 'telegram'), ('address', 'address')], max_length=50, verbose_name='type'),
        ),
    ]
