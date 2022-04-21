from django.contrib import admin

# Register your models here.
from payment.models import Transaction, Tariff, ReplenishmentModel


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'user', 'provider', 'amount', 'purpose', 'status', 'date')
    readonly_fields = ('order_id', 'paybox_id', 'user', 'provider', 'amount', 'currency', 'action', 'purpose', 'status', 'tariff',
                       'period')
    search_fields = ('user', 'provider', 'status', 'provider')
    ordering = ('-date',)


@admin.register(Tariff)
class TariffAdmin(admin.ModelAdmin):
    list_display = ('amount', 'currency', 'title_ru', 'title_ky', 'period')


@admin.register(ReplenishmentModel)
class TariffAdmin(admin.ModelAdmin):
    list_display = ('id', 'price')