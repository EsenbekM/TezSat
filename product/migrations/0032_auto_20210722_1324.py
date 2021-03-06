# Generated by Django 3.1.3 on 2021-07-22 07:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0031_productreview_is_read'),
    ]

    operations = [
        migrations.CreateModel(
            name='ClaimCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('icon', models.ImageField(upload_to='claim/icon', verbose_name='icon')),
                ('claim_type', models.CharField(max_length=50, verbose_name='type')),
            ],
            options={
                'db_table': 'claim_category',
            },
        ),
        migrations.AddField(
            model_name='claim',
            name='type',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='claim_category', to='product.claimcategory', verbose_name='claim_category'),
        ),
    ]
