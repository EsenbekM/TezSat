# Generated by Django 3.1.3 on 2021-08-06 10:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0032_auto_20210722_1324'),
    ]

    operations = [
        migrations.AddField(
            model_name='claimcategory',
            name='language',
            field=models.CharField(choices=[('ru', 'ru'), ('ky', 'ky')], default='ky', max_length=20),
        ),
    ]