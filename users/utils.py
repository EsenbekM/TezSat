from rest_framework.exceptions import AuthenticationFailed

from .models import User
from .settings import SignInMethods


def _parse_phone_provider(decoded) -> dict:
    return {
        "phone": decoded['phone_number'],
        "firebase_uid": decoded['uid'],
        "sign_in_method": SignInMethods.credentials
    }


def _parse_email_provider(decoded) -> dict:
    return {
        "email": decoded['email'],
        "firebase_uid": decoded['uid'],
        "sign_in_method": SignInMethods.credentials
    }


def _parse_social_provider(decoded) -> dict:
    return {
        "name": decoded['name'] if decoded.get('name') is not None else decoded.get('email'),
        "email": decoded.get('email'),
        "firebase_uid": decoded['uid'],
        "sign_in_method": SignInMethods.socials
    }


def _parse_facebook_provider(decoded) -> dict:
    """
    Example json coming from facebook

    Phone
    {
        'aud': 'tezsat-a824d',
        'auth_time': 1599629293,
        'exp': 1599632894,
        'firebase': {'identities': {'facebook.com': ['114328583742128']},
                  'sign_in_provider': 'facebook.com'},
        'iat': 1599629294,
        'iss': 'https://securetoken.google.com/tezsat-a824d',
        'name': 'Nursultan Abr',
        'picture': 'https://graph.facebook.com/114328583742128/picture',
        'sub': '83j7psfKMJgfUrC5IEKFkTQ8QSy1',
        'uid': '83j7psfKMJgfUrC5IEKFkTQ8QSy1',
        'user_id': '83j7psfKMJgfUrC5IEKFkTQ8QSy1'
    }

    Email
    {
        'aud': 'tezsat-a824d',
        'auth_time': 1599650398,
        'email': 'allinall05@gmail.com',
        'email_verified': False,
        'exp': 1599654003,
        'firebase': {'identities': {'email': ['allinall05@gmail.com'],
                                 'facebook.com': ['114908863678643']},
                  'sign_in_provider': 'facebook.com'},
        'iat': 1599650403,
        'iss': 'https://securetoken.google.com/tezsat-a824d',
        'name': 'Allinall Abr',
        'picture': 'https://graph.facebook.com/114908863678643/picture',
        'sub': 'mV0Vd6wBL6RO2VYEY1t24dePfiK2',
        'uid': 'mV0Vd6wBL6RO2VYEY1t24dePfiK2',
        'user_id': 'mV0Vd6wBL6RO2VYEY1t24dePfiK2'
    }
    """
    return {
        'facebook_uid': decoded['firebase']['identities']['facebook.com'][0],
        'email': decoded['firebase']['identities'].get('email', [None])[0],
        'firebase_uid': decoded['uid'],
        "sign_in_method": SignInMethods.socials,
        "name": decoded['name']
    }


def get_param_from_firebase(data):
    provider = data['firebase']['sign_in_provider']
    if provider == 'phone':
        return _parse_phone_provider(data), 'phone'
    elif provider == 'password':
        return _parse_email_provider(data), 'password'
    else:
        return None, None


def get_user_from_firebase(data):
    provider = data['firebase']['sign_in_provider']
    if provider == 'phone':
        params = _parse_phone_provider(data)
        exist = User.objects.filter(phone=params['phone'], phone__isnull=False).first()
    elif provider == 'password':
        params = _parse_email_provider(data)
        exist = User.objects.filter(email__iexact=params['email'], email__isnull=False).first()
    elif provider == 'anonymous':
        raise AuthenticationFailed('anonymous user is not allowed')
    elif provider == 'facebook.com':
        params = _parse_facebook_provider(data)
        if params.get('email'):
            exist = User.objects.filter(email__iexact=params['email']).first()
        else:
            exist = User.objects.filter(facebook_uid=params['facebook_uid']).first()
    else:
        try:
            params = _parse_social_provider(data)
            exist = User.objects.filter(email__iexact=params['email'], email__isnull=False).first()
        except Exception as e:
            print(e, data)
            raise NotImplementedError(f'unknown provider {provider}')
    if exist:
        return exist
    return params
