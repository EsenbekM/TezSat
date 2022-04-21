from datetime import timedelta

from django.conf import settings
from django.utils.translation import gettext_lazy as _


class CurrencyType:
    USD = 'USD'
    KGS = 'KGS'

    @classmethod
    def choices(cls):
        return (
            (cls.USD, cls.USD),
            (cls.KGS, cls.KGS)
        )

    @classmethod
    def all(cls):
        return cls.USD, cls.KGS


class SellerType:
    OWNER = 'owner'
    RESELLER = 'reseller'

    @classmethod
    def choices(cls):
        return (
            (cls.OWNER, _(cls.OWNER)),
            (cls.RESELLER, _(cls.RESELLER))
        )


class ProductState:
    ACTIVE = 'active'
    INACTIVE = 'inactive'
    DELETED = 'deleted'
    BLOCKED = 'blocked'
    ON_REVIEW = 'on_review'

    @classmethod
    def choices(cls):
        return (
            (cls.ACTIVE, _(cls.ACTIVE)),
            (cls.INACTIVE, _(cls.INACTIVE)),
            (cls.DELETED, _(cls.DELETED)),
            (cls.BLOCKED, _(cls.BLOCKED)),
            (cls.ON_REVIEW, _('on review'))
        )


PHOTO_UPLOAD_DIR = 'products/photo'
SMALL_THUMBNAIL_DIR = 'products/small_thumbnail'
MEDIUM_THUMBNAIL_DIR = 'products/medium_thumbnail'
PHOTO_TMP_DIR = 'products/tmp'
ICON = 'claim/icon'

PHOTO_TMP_LIFE_PERIOD = getattr(settings, 'PRODUCT_PHOTO_LIFE_TIME', timedelta(minutes=10))

PRODUCT_UPVOTE_LIMIT = settings.PRODUCT_UPVOTE_LIMIT
