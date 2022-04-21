# Generated by Django 3.0.6 on 2020-07-06 09:51

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('product', '0014_auto_20200706_1330'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductReview',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.PositiveSmallIntegerField(choices=[(1, '☆'), (2, '☆ ☆'), (3, '☆ ☆ ☆'), (4, '☆ ☆ ☆ ☆'), (5, '☆ ☆ ☆ ☆ ☆')], verbose_name='rating')),
                ('review', models.TextField(verbose_name='review')),
                ('creation_date', models.DateTimeField(auto_now_add=True)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to='product.Product', verbose_name='product')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to=settings.AUTH_USER_MODEL, verbose_name='user')),
            ],
            options={
                'db_table': 'product_review',
                'unique_together': {('product', 'user')},
            },
        ),
    ]
