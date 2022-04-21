# Generated by Django 3.0.6 on 2020-07-10 10:01

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('business', '0003_business_rating'),
    ]

    operations = [
        migrations.CreateModel(
            name='BusinessRequest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='name')),
                ('phone', phonenumber_field.modelfields.PhoneNumberField(max_length=128, region=None, verbose_name='phone')),
                ('message', models.TextField(blank=True, null=True, verbose_name='message')),
                ('date', models.DateTimeField(auto_now_add=True, verbose_name='date')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='business_requests', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'business_request',
            },
        ),
    ]