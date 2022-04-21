# Generated by Django 3.1.1 on 2020-10-10 06:44

from django.db import migrations, models
import product.models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0023_delete_productlike'),
    ]

    operations = [
        migrations.AddField(
            model_name='productphoto',
            name='medium_thumbnail',
            field=models.ImageField(null=True, upload_to=product.models.medium_thumbnail_upload_to, verbose_name='medium thumbnail'),
        ),
        migrations.AddField(
            model_name='productphoto',
            name='small_thumbnail',
            field=models.ImageField(null=True, upload_to=product.models.small_thumbnail_upload_to, verbose_name='thumbnail'),
        ),
    ]
