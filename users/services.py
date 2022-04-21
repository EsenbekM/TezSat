from django.utils import timezone
from rest_framework.exceptions import AuthenticationFailed
from datetime import datetime as dt

from users.models import User
from users.settings import SignInMethods, RequestStatuses
from users.utils import _parse_phone_provider, _parse_facebook_provider, _parse_email_provider, _parse_social_provider
from json2xml import json2xml

from json2xml.utils import readfromurl, readfromstring, readfromjson
import requests
from decouple import config


def firebase_login(validated_data) -> User:
    decoded = validated_data['decoded']
    user = User.objects.filter(firebase_uid=decoded['user_id']).first()
    if user:
        user.sign_in_method = SignInMethods.socials
        user.provider = decoded['firebase']['sign_in_provider']
        user.save()
        return user
    else:
        user_data = _prepare_user_data(validated_data)
        user = User(**user_data)
        user.last_login = timezone.now()
        user.save()
        return user


def _prepare_user_data(validated_data):
    provider_parsers = {
        'phone': _parse_phone_provider,
        'facebook.com': _parse_facebook_provider,
        'email': _parse_email_provider,
        'google.com': _parse_social_provider,
    }
    language = validated_data['language']
    decoded = validated_data['decoded']
    provider = decoded['firebase']['sign_in_provider']
    phone = validated_data.get('phone', None)

    if provider in provider_parsers:
        parser_function = provider_parsers[provider]
        return {
            'language': language,
            'phone': phone,
            'provider': provider,
            **parser_function(decoded),
        }
    else:
        raise AuthenticationFailed('anonymous or unknown provider is not allowed')


def get_translit_word(param, parent=None):
    char_dict = {'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo',
                 'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'i', 'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n',
                 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u', 'ф': 'f', 'х': 'h',
                 'ц': 'c', 'ч': 'ch', 'ш': 'sh', 'щ': 'sch', 'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e',
                 'ю': 'u', 'я': 'ya', " ": " ", ',': ''
                 }

    m = [char_dict.get(i, i) for i in param.lower()]
    m = "".join(m)
    if parent:
        p = [char_dict.get(i, i) for i in parent.lower()]
        p = "".join(p)
        m = f"{p} {m}"
    return m


def _send_to_the_code(id, code, phone):
    api = 'http://smspro.nikita.kg/api/message'
    data = readfromstring(
        '{"login": "%s", '
        '"pwd": "%s", '
        '"id": "%s", '
        '"sender": "tezsat.kg", '
        '"text": "%s",'
        '"phones": {"phone": "%s"}}' % (config('PAYBOX_LOGIN'), config('PAYBOX_PASSWORD'), id, code, phone))
    data = json2xml.Json2xml(data=data, wrapper='message', pretty=True, attr_type=False).to_xml()
    response = requests.post(url=api, data=data)
    return response

def expired_limit_(instance):
    ex = instance.remove_layout
    if instance.request_status != RequestStatuses.ACCEPTED:
        try:
            if dt.now().date() >= ex:
                if instance.request_status == RequestStatuses.NOT_REQUESTED:
                    instance.request_status = RequestStatuses.NOT_REQUEST_NONE
                elif instance.request_status == RequestStatuses.EXPIRED:
                    instance.request_status = RequestStatuses.EXPIRED_NONE
            instance.save()
        except TypeError:
            pass
    return instance.request_status