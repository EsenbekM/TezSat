import os
from copy import deepcopy

from django.core.files.storage import default_storage
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django_q.tasks import async_task
from phonenumber_field.modelfields import PhoneNumberField

from notification.job import activated, blocked
from tezsat.push_texts import PushText, PushBody
from tezsat.settings import Lang
from tezsat.utils import get_filename, compress_image
from .settings import CurrencyType, ProductState, PHOTO_UPLOAD_DIR, MEDIUM_THUMBNAIL_DIR, SMALL_THUMBNAIL_DIR, \
    ICON


class Rate(models.Model):
    class Meta:
        db_table = 'rate'

    currency = models.CharField(_('title'), max_length=5, choices=CurrencyType.choices(), null=False, unique=True)
    rate = models.DecimalField(_('rate'), null=False, max_digits=20, decimal_places=2, default=0)
    last_update = models.DateTimeField(_('last update time'), auto_now=True)

    def __str__(self):
        return str(self.currency)


class Product(models.Model):
    class Meta:
        db_table = 'product'
        ordering = ('-upvote_date',)

    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='products', null=False,
                             verbose_name=_('user'))
    title = models.CharField(_('title'), max_length=50, null=False, db_index=True)
    description = models.TextField(_('description'), null=False)
    location = models.ForeignKey('location.Location', on_delete=models.PROTECT, null=False, related_name='products',
                                 verbose_name=_('location'))
    currency = models.CharField(_('currency'), max_length=5, choices=CurrencyType.choices(), null=False)
    price_kgs = models.DecimalField(_('price in kgs'), null=False, max_digits=20, decimal_places=0)
    price_usd = models.DecimalField(_('price in usd'), null=False, max_digits=20, decimal_places=2)
    initial_price = models.DecimalField(_('initial price'), null=False, max_digits=20, decimal_places=2)
    category = models.ForeignKey('category.Category', on_delete=models.PROTECT, related_name='products', null=False,
                                 verbose_name=_('category'))
    state = models.CharField(_('state'), choices=ProductState.choices(), null=False, default=ProductState.ON_REVIEW,
                             max_length=20)
    creation_date = models.DateTimeField(_('creation date'), auto_now_add=True)
    upvote_date = models.DateTimeField(_('upvote date'), auto_now_add=True)
    show_count = models.PositiveIntegerField(_('show count'), default=0, null=False)
    view_count = models.PositiveIntegerField(_('view count'), default=0, null=False)

    rating = models.PositiveSmallIntegerField(_('rating'), null=True)
    rating_disabled = models.BooleanField(_('rating disabled'), null=False, blank=False, default=True)

    call_count = models.PositiveIntegerField(_('call count'), null=False, default=0)
    message_count = models.PositiveIntegerField(_('message count'), null=False, default=0)
    # скидка
    discount_price_kgs = models.DecimalField(_('discount_price_kgs'), max_digits=20, decimal_places=2, null=True,
                                             blank=True)
    discount_price_usd = models.DecimalField(_('discount_price_usd'), max_digits=20, decimal_places=2, null=True,
                                             blank=True)
    discount = models.IntegerField(_("discount"), null=True, blank=True)

    @property
    def price(self):
        return self.initial_price

    @price.setter
    def price(self, value):
        self.initial_price = value

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.state_ = self.state
        self.initial_price_ = deepcopy(self.initial_price)

    def __str__(self):
        return str(self.title)

    def save(self, *args, **kwargs):
        self.title = self.description[:50]
        if not self.id or self.initial_price != self.initial_price_:
            usd = Rate.objects.filter(currency=CurrencyType.USD).first()
            if not usd:
                usd = Rate.objects.create(currency=CurrencyType.USD, rate=1)
            if self.currency == CurrencyType.USD:
                self.price_usd = self.initial_price
                self.price_kgs = self.initial_price * usd.rate
            else:
                self.price_kgs = self.initial_price
                self.price_usd = self.initial_price / usd.rate
        if self.state_ != self.state:
            if self.state == ProductState.ACTIVE:
                if not hasattr(self.user, 'business'):
                    activated(self)
                self.upvote_date = timezone.now()
            if self.state == ProductState.BLOCKED:
                blocked(self)
        # make business products active on creation
        if hasattr(self.user, 'business') and self.user.business.is_active and self.pk is None:
            self.state = ProductState.ACTIVE
        super().save(*args, **kwargs)


class ProductReview(models.Model):
    class Meta:
        db_table = 'product_review'
        unique_together = ('product', 'user')

    product = models.ForeignKey('Product', related_name='reviews', null=False, on_delete=models.CASCADE,
                                verbose_name=_('product'))
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='reviews', null=False,
                             verbose_name=_('user'))
    rating = models.PositiveSmallIntegerField(_('rating'), choices=((1, '☆'),
                                                                    (2, '☆ ☆'),
                                                                    (3, '☆ ☆ ☆'),
                                                                    (4, '☆ ☆ ☆ ☆'),
                                                                    (5, '☆ ☆ ☆ ☆ ☆')), null=False)
    review = models.TextField(_('review'), null=False)
    response = models.TextField(_('response'), null=True)
    response_date = models.DateTimeField(null=True)
    creation_date = models.DateTimeField(auto_now_add=True, null=False)
    claim = models.TextField(_('claim'), null=True, blank=True)
    claim_date = models.DateTimeField(null=True)
    is_read = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.pk:
            lang = self.user.language
            self.user.push_new_comment(title=PushText.new_review[lang], message=PushBody.new_review[lang],
                                       data={"product_id": str(self.product.id)})
        super().save(*args, **kwargs)

    def __str__(self):
        return self.review

class ReviewClaimProxy(ProductReview):
    class Meta:
        verbose_name = 'Review Claim'
        verbose_name_plural = 'Review Claims'
        proxy = True


class ProductContact(models.Model):
    class Meta:
        db_table = 'product_contact'

    product = models.ForeignKey('Product', related_name='contacts', null=False, on_delete=models.CASCADE,
                                verbose_name=_('product'))
    phone = PhoneNumberField(_('phone number'), null=False)


def photo_upload_to(instance, filename):
    new_filename = get_filename(filename)
    return os.path.join(PHOTO_UPLOAD_DIR, new_filename)


def small_thumbnail_upload_to(instance, filename):
    new_filename = get_filename(filename)
    return os.path.join(SMALL_THUMBNAIL_DIR, new_filename)


def medium_thumbnail_upload_to(instance, filename):
    new_filename = get_filename(filename)
    return os.path.join(MEDIUM_THUMBNAIL_DIR, new_filename)


class ProductPhoto(models.Model):
    class Meta:
        db_table = 'product_photo'

    product = models.ForeignKey('Product', related_name='photos', null=False, on_delete=models.CASCADE,
                                verbose_name=_('product'))
    photo = models.ImageField(_('photo'), null=False, upload_to=photo_upload_to)
    small_thumbnail = models.ImageField(_('thumbnail'), null=True, upload_to=small_thumbnail_upload_to)
    medium_thumbnail = models.ImageField(_('medium thumbnail'), null=True, upload_to=medium_thumbnail_upload_to)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.photo_ = deepcopy(self.photo)

    def save(self, *args, **kwargs):
        if self.photo and self.photo != self.photo_:
            self.photo = compress_image(self.photo)
            self.small_thumbnail = compress_image(self.photo, is_small_thumbnail=True)
            self.medium_thumbnail = compress_image(self.photo, is_medium_thumbnail=True)
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.photo:
            async_task(default_storage.delete, self.photo.name, task_name='remove old photo')
        if self.medium_thumbnail:
            async_task(default_storage.delete, self.medium_thumbnail.name, task_name='remove medium thumbnail')
        if self.small_thumbnail:
            async_task(default_storage.delete, self.small_thumbnail.name, task_name='remove small thumbnail')
        super().delete(*args, **kwargs)


class ProductParameter(models.Model):
    class Meta:
        db_table = 'product_parameter'

    product = models.ForeignKey('Product', related_name='parameters', null=False, on_delete=models.CASCADE,
                                verbose_name=_('product'))
    parameter = models.ForeignKey('category.Parameter', on_delete=models.CASCADE, null=False,
                                  verbose_name=_('parameter'))
    option = models.ForeignKey('category.Option', on_delete=models.CASCADE, null=True, blank=True,
                               verbose_name=_('option'))
    response = models.CharField(_('response'), max_length=100, null=True, blank=True)


class Claim(models.Model):
    class Meta:
        db_table = 'product_claim'
        unique_together = ('product', 'user')
        verbose_name = 'Product Claim'
        verbose_name_plural = 'Product Claims'

    product = models.ForeignKey('Product', related_name='claims', null=False, on_delete=models.CASCADE,
                                verbose_name=_('product'))
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='claims', null=False,
                             verbose_name=_('user'))
    type = models.ForeignKey('ClaimCategory', on_delete=models.CASCADE, verbose_name='claim_category',
                             related_name='claim_category', null=True)
    message = models.CharField(_('message'), max_length=200, null=False, blank=False)
    creation_date = models.DateTimeField(_('creation date'), auto_now_add=True)

    def __str__(self):
        return self.message


class ClaimCategory(models.Model):
    class Meta:
        db_table = 'claim_category'

    icon = models.ImageField(_('icon'), null=False, upload_to=ICON)
    claim_type = models.CharField(_('type'), max_length=50, null=False, blank=False)
    language = models.CharField(max_length=20, choices=Lang.choices(), default=Lang.KY)

    def __str__(self):
        return self.claim_type


class Keyword(models.Model):
    """
    Storing keywords for search terms
    """
    keyword = models.CharField(max_length=255)
    is_search = models.BooleanField(default=False)

    def __str__(self):
        return self.keyword
