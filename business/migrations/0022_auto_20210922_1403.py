# Generated by Django 3.1.3 on 2021-09-22 08:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('business', '0021_business_is_not_demo'),
    ]

    operations = [
        migrations.CreateModel(
            name='AddModal',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('date', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'db_table': 'add_modal',
            },
        ),
        migrations.AlterField(
            model_name='business',
            name='is_not_demo',
            field=models.BooleanField(default=False, verbose_name='is not demo'),
        ),
    ]
