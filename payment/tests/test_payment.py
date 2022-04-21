import datetime
import random

import pytest
from django.urls import reverse
from rest_framework import status

from payment.models import Transaction
from product.settings import CurrencyType


@pytest.fixture
def get_link(create_full_business, api_client, tariff_factory):
    business = create_full_business
    api_client.force_authenticate(user=business.user)
    tariff = tariff_factory()
    url = reverse('init_payment')

    def _func(action: str):
        payload = {'amount': 15000}
        if action != 'replenishment':
            payload['action'] = 'purchase'
            payload['tariff_id'] = tariff.id
        else:
            payload['action'] = 'replenishment'
        response = api_client.post(url, data=payload, format='json')
        response.data['tariff'] = tariff
        response.data['business'] = business
        return response.data

    return _func

def _method(transaction, tariff, result: int) -> dict:
    now = datetime.datetime.now()
    payload = {
        'pg_order_id': transaction.order_id,
        'pg_payment_id': random.randint(123200, 1204239),
        'pg_currency': CurrencyType.KGS,
        'pg_payment_system': 'VISA',
        'pg_description': 'Оплата за %s мес' % tariff if transaction.action == 'purchase' else 'Пополнение',
        'pg_payment_date': '%s' % now,
        'pg_result': f'{result}',
        'pg_salt': "email.com, ",
        'time': now
    }
    return payload

@pytest.mark.parametrize(
    'action', [
        ('purchase'),
        ('replenishment'),

    ]
)
@pytest.mark.django_db
def test_link(get_link, action):
    get_link = get_link(action)
    assert get_link['link'] != ''

@pytest.mark.django_db
def test_success_purchase(get_link,  user_factory, api_client, tariff_factory):

    get_link = get_link('purchase')
    tariff = get_link['tariff']
    url = reverse('result_url')
    transaction = Transaction.objects.last()
    payload = _method(transaction, tariff.period, result=1)
    response = api_client.post(url, data=payload, format='json')
    assert response.status_code == status.HTTP_200_OK
    transaction = Transaction.objects.last()

    assert transaction.status == 'paid'
    assert transaction.amount == 15000
    # deactivate_date = datetime.datetime.now() + datetime.timedelta(weeks=4*tariff.period)
    # assert transaction.user.business.deactivate_date.date() == deactivate_date.date()

@pytest.mark.django_db
def test_not_successful_purchase(get_link, api_client):

    get_link = get_link('purchase')
    tariff = get_link['tariff']
    business = get_link['business']
    url = reverse('result_url')
    transaction = Transaction.objects.last()
    payload = _method(transaction, tariff.period, result=0)

    response = api_client.post(url, payload, format='json')

    assert response.status_code == status.HTTP_200_OK
    transaction = Transaction.objects.last()

    assert transaction.status == 'canceled'
    # assert business.deactivate_date == None


@pytest.mark.django_db
@pytest.mark.parametrize(
    'result', [
        (1),
        (0)
    ]
)
def test_success_replenishment(get_link, result, api_client):

    get_link = get_link('replenishment')
    assert get_link['link'] != ''

    url = reverse('result_url')
    transaction = Transaction.objects.last()
    payload = _method(transaction, tariff=None, result=result)
    response = api_client.post(url, data=payload, format='json')
    assert response.status_code == status.HTTP_200_OK
    if result == 1:
        assert transaction.user.balance == 15000
    else:
        assert transaction.user.balance == 0


