# Generated by Django 3.1.3 on 2020-12-01 22:58

import business.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('business', '0012_businessbranch'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='businessbranch',
            name='location',
        ),
        migrations.AddField(
            model_name='businessbranch',
            name='lat',
            field=models.DecimalField(decimal_places=6, default='74.961125', max_digits=9, verbose_name='longitude'),
        ),
        migrations.AddField(
            model_name='businessbranch',
            name='lng',
            field=models.DecimalField(decimal_places=6, default='74.961125', max_digits=9, verbose_name='longitude'),
        ),
        migrations.CreateModel(
            name='BusinessBanner',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('photo', models.ImageField(upload_to=business.models.banners_upload_to, verbose_name='photo')),
                ('text', models.CharField(blank=True, max_length=200, null=True, verbose_name='text')),
                ('business', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='banners', to='business.business')),
            ],
            options={
                'db_table': 'business_banners',
            },
        ),
    ]
