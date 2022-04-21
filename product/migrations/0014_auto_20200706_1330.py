# Generated by Django 3.0.6 on 2020-07-06 07:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0013_auto_20200514_1253'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='dislike_count',
            field=models.PositiveIntegerField(default=0, verbose_name='dislike_count'),
        ),
        migrations.AddField(
            model_name='product',
            name='like_count',
            field=models.PositiveIntegerField(default=0, verbose_name='like count'),
        ),
    ]