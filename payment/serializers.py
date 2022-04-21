from rest_framework import serializers as s
from rest_framework.exceptions import ValidationError

from notification.models import Notification
from notification.settings import NotificationAction as N_A
from tezsat.push_texts import PushText, PushBody
from tezsat.settings import Lang
from . import models
from .models import Tariff
from .services import get_tariff, _payment


class InitialPayment(s.ModelSerializer):
    class Meta:
        model = models.Transaction
        fields = ('user', 'amount', 'action')
        read_only_fields = ()


class ResultSerializers(s.Serializer):
    pg_order_id = s.CharField()  # Идентификатор заказа в системе мерчанта
    pg_payment_id = s.CharField()  # Внутренний идентификатор платежа в системе PayBox.money||integer
    pg_currency = s.CharField(required=False)
    pg_payment_system = s.CharField(required=False)
    pg_description = s.CharField(required=False)
    pg_result = s.IntegerField()
    pg_salt = s.CharField(required=False)


class PaymentFromWalletSerializer(s.ModelSerializer):
    tariff_id = s.IntegerField(required=False)
    amount = s.IntegerField()
    period = s.IntegerField(required=False)

    class Meta:
        model = models.Transaction
        fields = ('tariff_id', 'amount', 'period')

    def validate(self, attrs):
        user = self.context['user']
        if user.balance < attrs['amount']:
            raise ValidationError('Недостаточно средств')
        user.update_balance(balance=attrs['amount'], status='minus')
        if 'period' not in attrs:
            period = Tariff.objects.filter(id=attrs.get('tariff_id')).first().period
        else:
            period = attrs.get('period')
        title = PushText.payment_title[user.language]
        body = PushBody.payment_body[user.language]
        user.send_message(title=title, body=body, status='payment')
        n_data = {'title_ky': PushText.payment_title[Lang.KY],
                  'title_ru': PushText.payment_title[Lang.RU],
                  'description_ky': PushBody.payment_body[Lang.KY],
                  'description_ru': PushBody.payment_body[Lang.RU]}
        Notification.objects.create(receiver=user, **n_data, action=N_A.PAYMENT)
        _payment(user=user, tariff=period)
        attrs['user'] = user
        attrs['period'] = period
        return attrs

    def create(self, validated_data):
        validated_data['action'] = 'purchase'
        validated_data['provider'] = 'balance'
        validated_data['status'] = 'paid'
        validated_data['currency'] = 'KGS'
        return models.Transaction.objects.create(**validated_data)


class SuccessSerializers(s.ModelSerializer):
    class Meta:
        model = models.Transaction
        fields = ('user', 'amount', 'action', 'date', 'order_id', 'paybox_id', 'status')

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.action == 'replenishment':
            data["success"] = 'Ваш кошелек пополнен'
        else:
            data["success"] = 'Вы оплатили Бизнес акккаунт'
        return data


class TariffSerializers(s.ModelSerializer):
    class Meta:
        model = models.Tariff
        fields = ('id', 'amount', 'title_ru', 'title_ky', 'currency', 'period')

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['name'] = instance.name_kgz if self.context['request'].user.language == Lang.KY else instance.name_ru
        return data


class TransactionsSerializer(s.ModelSerializer):
    class Meta:
        model = models.Transaction
        fields = ('order_id', 'paybox_id', 'action', 'amount', 'currency', 'tariff', 'date', 'period')

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['tariff'] = get_tariff(request=self.context['request'], tariff=instance.tariff)
        return data


class ReplenishmentSerializer(s.ModelSerializer):
    class Meta:
        model = models.ReplenishmentModel
        fields = ('id', 'price')

    # def to_representation(self, instance):
    #     data = super().to_representation(instance)
    #     data['is_other'] = False
    #     return data
