# Generated by Django 3.1.3 on 2021-06-10 09:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ads', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='advertisement',
            name='image_link',
            field=models.ImageField(upload_to='abc/'),
        ),
    ]
