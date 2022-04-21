# Generated by Django 3.1.3 on 2021-09-20 11:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0033_claimcategory_language'),
    ]

    operations = [
        migrations.CreateModel(
            name='ReviewClaimProxy',
            fields=[
            ],
            options={
                'verbose_name': 'Review Claim',
                'verbose_name_plural': 'Review Claims',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('product.productreview',),
        ),
        migrations.AlterModelOptions(
            name='claim',
            options={'verbose_name': 'Product Claim', 'verbose_name_plural': 'Product Claims'},
        ),
    ]