# Generated by Django 3.1.3 on 2021-08-30 04:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0033_claimcategory_language'),
        ('notification', '0008_pushnotification_business'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='description',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='description'),
        ),
        migrations.AddField(
            model_name='notification',
            name='title',
            field=models.CharField(blank=True, max_length=30, null=True, verbose_name='title'),
        ),
        migrations.AlterField(
            model_name='notification',
            name='action',
            field=models.CharField(choices=[('activated', 'activated'), ('stared', 'stared'), ('blocked', 'blocked'), ('payment', 'payment')], max_length=50, verbose_name='action'),
        ),
        migrations.AlterField(
            model_name='notification',
            name='product',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='product.product'),
        ),
    ]