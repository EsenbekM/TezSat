# Generated by Django 3.1.3 on 2021-09-30 05:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('category', '0008_category_title_slug'),
    ]

    operations = [
        migrations.CreateModel(
            name='CategoryFixture',
            fields=[
            ],
            options={
                'verbose_name': 'Parent category',
                'verbose_name_plural': 'Parents category',
                'ordering': ('order',),
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('category.category',),
        ),
    ]
