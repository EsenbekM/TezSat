# Generated by Django 3.1.3 on 2021-06-21 10:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0026_create_custom_index'),
    ]

    operations = [
        migrations.AddField(
            model_name='keyword',
            name='is_search',
            field=models.BooleanField(default=False),
        ),
    ]