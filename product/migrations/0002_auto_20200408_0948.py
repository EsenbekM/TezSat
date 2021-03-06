# Generated by Django 3.0.5 on 2020-04-08 09:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Rate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('currency', models.CharField(choices=[('USD', 'USD'), ('KGS', 'KGS')], max_length=5, verbose_name='title')),
                ('rate', models.DecimalField(decimal_places=2, max_digits=20, verbose_name='rate')),
            ],
            options={
                'db_table': 'rate',
            },
        ),
        migrations.AddField(
            model_name='product',
            name='initial_price',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=20, verbose_name='initial price'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='product',
            name='currency',
            field=models.CharField(choices=[('USD', 'USD'), ('KGS', 'KGS')], max_length=5, verbose_name='title'),
        ),
        migrations.DeleteModel(
            name='Currency',
        ),
    ]
