# Generated by Django 3.0.8 on 2020-08-20 11:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0018_product_rating_disabled'),
    ]

    operations = [
        migrations.AddField(
            model_name='productreview',
            name='response',
            field=models.TextField(null=True, verbose_name='response'),
        ),
        migrations.AddField(
            model_name='productreview',
            name='response_date',
            field=models.DateTimeField(null=True),
        ),
    ]
