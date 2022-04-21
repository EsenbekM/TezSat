from uuid import uuid4

from django.db import models

from product.models import Rate
from product.settings import CurrencyType
from users.models import User


# Create your models here.


class Transaction(models.Model):
    class Meta:
        db_table = 'transactions'

    action_choices = (
        ('replenishment', 'replenishment'),  # пополнение
        ('purchase', 'purchase'),  # покупка
    )

    status_choices = (
        ('paid', 'paid'),  # статус оплачен
        ('canceled', 'canceled'),  # статус отмены
        ('not paid', 'not paid'),  # статус не оплачен
    )

    order_id = models.UUIDField(primary_key=True, editable=False, default=uuid4)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                             related_name="transactions")  # user
    paybox_id = models.CharField(max_length=125, null=True, blank=True, verbose_name="id платежа в системе Paybox")
    currency = models.CharField(max_length=20, null=True, blank=True, verbose_name='Валюта')
    # поставщик
    provider = models.CharField(max_length=50, null=True)
    # сумма
    amount = models.IntegerField()
    # цель
    purpose = models.CharField(max_length=200, blank=True)
    # пополнения, покупка, возврат денег
    action = models.CharField(max_length=100, choices=action_choices)
    # дата платежа
    date = models.DateField(auto_now_add=True)
    # статус платежа по умолчанию False
    status = models.CharField(max_length=100, choices=status_choices, default='not paid')

    tariff = models.ForeignKey('Tariff', on_delete=models.CASCADE, related_name='tariff', null=True, blank=True)
    period = models.IntegerField('period', null=True, blank=True)

    def save(self, *args, **kwargs):
        super(Transaction, self).save(*args, **kwargs)

    def __str__(self):
        return f"user: {self.user}  amount: {self.amount} date: {self.date} paid: {self.status}"


class Tariff(models.Model):
    class Meta:
        db_table = 'tariff'

    amount = models.IntegerField()
    currency = models.CharField(max_length=10, choices=CurrencyType.choices(), default=CurrencyType.KGS)
    title_ru = models.CharField('ru', max_length=50, null=True, blank=False)
    title_ky = models.CharField('kgz', max_length=50, null=True, blank=False)
    period = models.IntegerField('На сколько месяцев')


class ReplenishmentModel(models.Model):
    class Meta:
        db_table = 'replenishment_db'

    price = models.IntegerField()
    currency = models.CharField(max_length=10, choices=CurrencyType.choices(), default=CurrencyType.KGS)
    # price_usd = models.IntegerField()

# @receiver(post_save, sender=Tariff)
# def post_save_tariff(sender, created, instance, **kwargs):
#     post_save.disconnect(post_save_tariff, sender=sender)
#     if created:
#         usd = Rate.objects.get(currency=CurrencyType.USD)
#         if instance.currency == CurrencyType.KGS:
#             amount = int(instance.amount / usd.rate)
#             currency = CurrencyType.USD
#         else:
#             amount = int(instance.amount * usd.rate)
#             currency = CurrencyType.KGS
#
#         sender.objects.create(amount=amount, currency=currency, name=instance.name, period=instance.period)
#         post_save.connect(post_save_tariff, sender=sender)
