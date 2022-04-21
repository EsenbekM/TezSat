# Generated by Django 3.1.3 on 2021-08-07 20:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0004_auto_20210712_1837'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tariff',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.IntegerField()),
                ('currency', models.CharField(choices=[('USD', 'USD'), ('KGS', 'KGS')], default='KGS', max_length=10)),
                ('name', models.CharField(max_length=50)),
                ('period', models.IntegerField(verbose_name='период по месяцам')),
            ],
            options={
                'db_table': 'tariff',
            },
        ),
        migrations.RemoveField(
            model_name='transaction',
            name='balance',
        ),
        migrations.DeleteModel(
            name='Balance',
        ),
    ]