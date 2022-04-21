PROFILE_UPLOAD_DIR = 'users/profile'

from tezsat.settings import Lang
from tezsat.push_texts import PushText


class RequestStatuses:
    ON_REVIEW = 'on_review'
    SUCCESS = 'success'
    ACCEPTED = 'accepted'
    NOT_REQUESTED = 'not_requested'
    EXPIRED = 'expired'
    NOT_REQUEST_NONE = 'not_request_none'
    EXPIRED_NONE = 'expired_none'
    NORMAL = 'normal'

    @classmethod
    def choices(cls):
        return (
            (cls.NOT_REQUESTED, cls.NOT_REQUESTED),
            (cls.ACCEPTED, cls.ACCEPTED),
            (cls.SUCCESS, cls.SUCCESS),
            (cls.ON_REVIEW, cls.ON_REVIEW),
            (cls.EXPIRED, cls.EXPIRED),
            (cls.NOT_REQUEST_NONE, cls.NOT_REQUEST_NONE),
            (cls.EXPIRED_NONE, cls.EXPIRED_NONE),
            (cls.NORMAL, cls.NORMAL)
        )


class Platforms:
    ios = 'ios'
    android = 'android'

    @classmethod
    def choices(cls):
        return (
            (cls.ios, cls.ios),
            (cls.android, cls.android)
        )


class SignInMethods:
    credentials = 'credentials'
    socials = 'socials'

    @classmethod
    def choices(cls):
        return (
            (cls.credentials, cls.credentials),
            (cls.socials, cls.socials)
        )


manager_apps = {'product', 'users', 'category', 'location'}
manager_permissions = {
    'product': {'change', 'view', 'add'},
    'users': {'view'},
    'category': {'view', 'add', 'change', 'delete'},
    'location': {'view', 'add', 'change', 'delete'},
}
