# Generated by Django 3.0.6 on 2020-07-09 07:06

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('category', '0006_auto_20200514_1253'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Business',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='name')),
                ('description', models.TextField(blank=True, null=True, verbose_name='description')),
                ('creation_date', models.DateTimeField(auto_now_add=True)),
                ('banner', models.ImageField(null=True, upload_to='', verbose_name='banner')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='businesses', to='category.Category')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='business', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'business',
            },
        ),
        migrations.CreateModel(
            name='BusinessSchedule',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('weekday', models.CharField(choices=[('monday', 'пн'), ('tuesday', 'вт'), ('wednesday', 'ср'), ('thursday', 'чт'), ('friday', 'пт'), ('saturday', 'сб'), ('sunday', 'вс')], max_length=20, verbose_name='weekday')),
                ('time', models.CharField(max_length=20, verbose_name='time')),
                ('business', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='schedule', to='business.Business')),
            ],
            options={
                'db_table': 'business_schedule',
            },
        ),
        migrations.CreateModel(
            name='BusinessContact',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('phone', 'phone'), ('email', 'email'), ('website', 'website'), ('facebook', 'facebook'), ('instagram', 'instagram'), ('whatsapp', 'whatsapp'), ('telegram', 'telegram')], max_length=50, verbose_name='type')),
                ('value', models.CharField(max_length=50, verbose_name='value')),
                ('business', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='contacts', to='business.Business')),
            ],
            options={
                'db_table': 'business_contact',
            },
        ),
    ]
