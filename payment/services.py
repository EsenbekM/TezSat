import datetime
import logging
import os
from datetime import datetime as DT
import hashlib
import requests
from django.core.mail import EmailMultiAlternatives
from django_q.tasks import async_task

from json2xml import json2xml

from json2xml.utils import readfromurl, readfromstring, readfromjson
logging.getLogger("django-q")


from business.models import Business
from category.models import Category
from tezsat.settings import Lang
from users.settings import RequestStatuses

pg_merchant_id = 538732
secret = 'qfH9YCLmfMN4cSQq'


def payment(pg_order_id, pg_amount, pg_description, pg_salt):
    pg_amount = pg_amount
    pg_description = pg_description
    pg_order_id = pg_order_id
    pg_salt = pg_salt
    pg_testing_mode = 0
    pg_result_url = 'http://api.tezsat.kg/payment/v1/result_url/'
    pg_success_url = 'https://app.tezsat.kg/profile/settings'
    pg_success_url_method = 'GET'

    signature = 'init_payment.php;%s;%s;%s;%s;%s;' \
                '%s;%s;%s;%s;%s' % (
                    pg_amount, pg_description,
                    pg_merchant_id, pg_order_id, pg_result_url,
                    pg_salt, pg_success_url, pg_success_url_method, pg_testing_mode, secret)
    sign = hashlib.md5(signature.encode())
    link = 'https://api.paybox.money/init_payment.php?pg_merchant_id=%s&pg_amount=%s&' \
           'pg_result_url=%s&' \
           'pg_salt=%s&' \
           'pg_success_url=%s&' \
           'pg_success_url_method=%s&' \
           'pg_order_id=%s&' \
           'pg_description=%s&' \
           'pg_testing_mode=%s&' \
           'pg_sig=%s' % (
               pg_merchant_id, pg_amount, pg_result_url, pg_salt, pg_success_url, pg_success_url_method,
               pg_order_id,
               pg_description,
               pg_testing_mode, sign.hexdigest())
    response = requests.get(link)
    text = response.text.replace("pg_redirect_url", "  ").split("  ")[1][1:-2]

    return text


def payment_answer(**kwargs):
    pg_sig = 'init_payment.php;%s;%s;%s;%s;' % (
        kwargs['status'], kwargs['pg_description'], kwargs['pg_salt'], pg_merchant_id)
    pg_sig = hashlib.md5(pg_sig.encode()).hexdigest()
    data = readfromstring('{"status": "%s", "pg_description": "%s", "pg_salt": "%s", "pg_sig": "%s"}' %
                          (kwargs['status'], kwargs['pg_description'], kwargs['pg_salt'], pg_sig))
    response = json2xml.Json2xml(data=data, wrapper='response', pretty=True, attr_type=False).to_xml()

    return response

def get_tariff(request, tariff):
    if request.user.language == Lang.RU:
        if tariff:
            tariff_ = tariff.period % 10
            month = 'месяца' if tariff_ in [2, 3, 4] else 'месяцев'
            if tariff_ == 1:
                month = 'месяц'
            answer = f'Оплата за {tariff.period} {month}'
        else:
            answer = 'Пополнение'
    else:
        answer = f'{tariff.period} айга толоо' if tariff else 'Толуктоо'
    return answer

def _payment(user, tariff) -> None:
    if hasattr(user, 'business'):
        business = user.business
    else:
        category = Category.objects.first()
        business = Business.objects.create(user=user, category=category)
    weeks = 4 * int(tariff)
    if business.deactivate_date is not None and business.deactivate_date.date() > DT.now().date():
        business.deactivate_date += datetime.timedelta(weeks=weeks)
    else:
        business.deactivate_date = DT.now() + datetime.timedelta(weeks=weeks)
    business.is_active = True
    business.save()
    user.request_status = RequestStatuses.SUCCESS
    user.save()
    return

logger = logging.getLogger("payment")

def logging_(msg) -> None:
    logger.info(f"{msg}")
    return
