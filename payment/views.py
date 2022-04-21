# Create your views here.
import datetime
import logging

from django.db.models import Q
from django_q.tasks import async_task
from rest_framework import generics, viewsets, status
from rest_framework import response
from rest_framework import mixins
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from  firebase_admin import firestore

from datetime import datetime as dt

from tezsat.settings import Lang

from notification.settings import NotificationAction as N_A

from django.db import transaction

from business.services import _prepare_date_range
from notification.models import Notification
from payment import services
from payment.models import Transaction, Tariff, ReplenishmentModel
from payment.renderers import UserJSONRenderer
from payment.serializers import InitialPayment, ResultSerializers, SuccessSerializers, TariffSerializers, \
    TransactionsSerializer, ReplenishmentSerializer, PaymentFromWalletSerializer
from payment.services import payment_answer, _payment, logging_
from tezsat.push_texts import PushText, PushBody


class InitPayment(mixins.CreateModelMixin, generics.GenericAPIView):
    serializer_class = InitialPayment
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        logging_(f"[init] - {request.data}")
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(    raise_exception=True)
        tariff = Tariff.objects.filter(id=request.data.get('tariff_id', None)).first()
        request.data.pop('tariff_id', None)
        transaction = Transaction.objects.create(user=request.user, **request.data, tariff=tariff)
        if 'period' not in request.data:
            description = 'Оплата за %s мес' % tariff.period if transaction.action == 'purchase' else 'Пополнение'
        else:
            description = 'Оплата за %s мес' % request.data['period']
        data = {
            'pg_order_id': transaction.order_id,
            'pg_amount': request.data["amount"],
            'pg_description': description,
            'pg_salt': '%s' % transaction.user.email
        }
        get_link = services.payment(**data)
        logging_(f"[init] - LINK CREATED")
        return Response(data={"link": get_link}, status=status.HTTP_200_OK)


class ResultUrl(generics.CreateAPIView):
    serializer_class = ResultSerializers
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        logging_(f"[Result] - {request.data}")
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = {
            'provider': request.data.get('pg_payment_system', None),
            'currency': request.data.get('pg_currency', None),
            'paybox_id': request.data['pg_payment_id'],
            'date': datetime.datetime.now().date(),
            'status': 'paid' if int(request.data["pg_result"]) else 'canceled'
        }
        with transaction.atomic():
            transaction_ = Transaction.objects.filter(order_id=request.data.get('pg_order_id'))
            transaction_copy = transaction_.first()
            answer = payment_answer(status='ok', pg_description='Заказ оплачен', pg_salt='спасибо за покупку')
            n_data = {'title_ky': PushText.payment_title[Lang.KY],
                      'title_ru': PushText.payment_title[Lang.RU],
                      'description_ky': PushBody.payment_body[Lang.KY],
                      'description_ru': PushBody.payment_body[Lang.RU]}
            logging_(f"[Result] - {transaction_copy.status}")
            if transaction_copy.status != 'paid':
                if data['status'] == 'paid':
                    user = transaction_copy.user
                    # purchase
                    if transaction_copy.action != 'replenishment':
                        period = request.data['pg_description'].split()[2]
                        title = PushText.payment_title[user.language]
                        body = PushBody.payment_body[user.language]
                        data['period'] = period
                        _payment(user=user, tariff=period)
                    # replenishment
                    else:
                        title = PushText.replenishment_title[user.language]
                        body = PushBody.replenishment_body[user.language] % transaction_copy.amount
                        n_data['title_ky'] = PushText.replenishment_title[Lang.KY]
                        n_data['title_ru'] = PushText.replenishment_title[Lang.RU]
                        n_data['description_ky'] = PushBody.replenishment_body[Lang.KY] % transaction_copy.amount
                        n_data['description_ru'] = PushBody.replenishment_body[Lang.RU] % transaction_copy.amount
                        user.update_balance(balance=transaction_copy.amount, status='plus')
                    transaction_.update(**data)
                    user.send_message(title=title, body=body, status='payment')
                    logging_(f"[Result] - SUCCESS PAYMENT")
                    Notification.objects.create(receiver=user, **n_data, action=N_A.PAYMENT)
                else:
                    logging_(f"[Result] - PAYMENT CANCELED")
                    transaction_.update(**data)
                    answer = payment_answer(status='rejected', pg_description='Платеж отменен',
                                            pg_salt='Заказ не оплачен')

        return Response(data=answer, status=status.HTTP_200_OK)


class PaymentFromWallet(generics.CreateAPIView):
    serializer_class = PaymentFromWalletSerializer
    permission_classes = (IsAuthenticated,)
    renderer_classes = (UserJSONRenderer,)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'user': request.user})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data={'message': 'ok'}, status=status.HTTP_200_OK)


class Replenishment(mixins.ListModelMixin,
                    viewsets.GenericViewSet):
    serializer_class = ReplenishmentSerializer
    pagination_class = None
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return ReplenishmentModel.objects.all()


class Payment(mixins.ListModelMixin,
              viewsets.GenericViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = TariffSerializers
    pagination_class = None

    def list(self, request, *args, **kwargs):
        serializer = self.get_serializer(Tariff.objects.all(), many=True, context={"request": self.request})
        return response.Response(serializer.data, status=status.HTTP_200_OK)


class TransactionsHistory(mixins.ListModelMixin,
                          viewsets.GenericViewSet):
    pagination_class = None
    permission_classes = (IsAuthenticated,)
    serializer_class = TransactionsSerializer

    def list(self, request, *args, **kwargs):
        start_date, end_date = request.query_params.get('start', ""), request.query_params.get('end', "")
        transactions = Transaction.objects.filter(user=request.user, status='paid').order_by('-date')
        data = {"history_list": []}
        if transactions:
            s_d = transactions.last().date
            s_d = int(datetime.datetime(year=s_d.year, month=s_d.month, day=s_d.day,
                                        hour=1, minute=1, second=1).timestamp())
            if start_date:
                start_date, end_date = int(start_date), int(end_date)
                date_range = _prepare_date_range(start_date, end_date)
            else:
                date_range = []
                now = dt.now().date()
                start = now - datetime.timedelta(days=7)
                date_range.append(Q(date__gte=start))
                date_range.append(Q(date__lte=now))
            transactions = transactions.filter(*date_range)
            serializer = self.get_serializer(transactions, many=True, context={"request": request})
            data["start_date"] = s_d
            data["history_list"] = *serializer.data,
        return response.Response(data, status=status.HTTP_200_OK)
