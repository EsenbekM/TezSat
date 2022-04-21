import datetime
import os
from copy import deepcopy
from datetime import datetime as dt

from django.core.files.storage import default_storage
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_q.tasks import async_task

from product.models import Product
from tezsat.utils import compress_image, get_filename
from users.models import User
from users.settings import RequestStatuses
from .settings import ContactType, Week, BANNER_UPLOAD_DIR, DEFAULT_BRANCH_LONGITUDE, DEFAULT_BRANCH_LATITUDE


def banners_upload_to(instance, filename):
    new_filename = get_filename(filename)
    return os.path.join(BANNER_UPLOAD_DIR, new_filename)


class Business(models.Model):
    class Meta:
        db_table = 'business'

    user = models.OneToOneField('users.User', on_delete=models.CASCADE, null=False, related_name='business')
    name = models.CharField(_('name'), null=False, max_length=200)
    description = models.TextField(_('description'), null=True, blank=True)
    creation_date = models.DateTimeField(auto_now_add=True, null=False)
    banner = models.ImageField(_('banner'), null=True, blank=True)
    category = models.ForeignKey('category.Category', on_delete=models.CASCADE, null=False, related_name='businesses')
    is_active = models.BooleanField(_('is active'), null=False, default=False)
    product_limit = models.PositiveSmallIntegerField(_('product limit'), null=True, blank=True)
    message = models.TextField(_('request message'), null=True, blank=True)
    deactivation_message = models.TextField(_('deactivation message'), null=True, blank=True)

    delivery = models.IntegerField(_('delivery'), null=True, blank=True)
    rating = models.SmallIntegerField(_('rating'), null=True)
    upvote_count = models.SmallIntegerField(_('auto upvote count'), null=False, default=2)

    logo = models.ImageField(_("logotype"), null=True, blank=True)
    deactivate_date = models.DateTimeField(_('Дата деактивации'), null=True, blank=True)
    is_not_demo = models.BooleanField(_('is not demo'), null=False, default=False)
    denied = models.BooleanField(_('denied business'), null=False, default=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.banner_ = deepcopy(self.banner)
        self.logo_ = deepcopy(self.logo)
        self.is_active_ = deepcopy(self.is_active)

    def save(self, *args, **kwargs):
        if not self.id:
            self.user.request_status = RequestStatuses.ON_REVIEW
            self.user.save()
        if self.user.request_status == RequestStatuses.ON_REVIEW and self.is_active:
            self.user.request_status = RequestStatuses.ACCEPTED
            self.user.save()

        if self.banner and self.banner != self.banner_:
            self.banner = compress_image(self.banner, business=True)
        if self.logo and self.logo != self.logo_:
            self.logo = compress_image(self.logo, quality=90, business=True)
        if self.is_active and not self.is_active_ and self.is_active != self.is_active_:
            if self.user.request_status not in [RequestStatuses.NOT_REQUESTED, RequestStatuses.NOT_REQUEST_NONE,
                                                RequestStatuses.ACCEPTED]:
                self.is_not_demo = True
            formats = '%Y-%m-%d %H:%M:%S'
            if not self.deactivate_date:
                self.deactivate_date = BusinessPeriod.objects.last().end_date
            end = dt.strptime(self.deactivate_date.strftime(formats), formats)
            if end <= dt.now() and self.is_not_demo != True:
                self.deactivate_date = dt.now() + datetime.timedelta(days=14)
                self.is_active = True
            self.user.push_business_activated()
            self.user.request_status = RequestStatuses.ACCEPTED
            self.user.save()
        # deactivated business
        elif self.is_active_ and not self.is_active and self.user != RequestStatuses.NOT_REQUEST_NONE:
            self.user.request_status = RequestStatuses.EXPIRED
            self.user.remove_layout = dt.now() + datetime.timedelta(days=10)
            self.user.save()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        async_task(default_storage.delete, self.banner.name, task_name='remove old photo')
        super().delete(*args, **kwargs)

    def __str__(self):
        return self.name


class BusinessContact(models.Model):
    class Meta:
        db_table = 'business_contact'

    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='contacts')
    type = models.CharField(_('type'), null=False, max_length=50, choices=ContactType.choices())
    value = models.CharField(_('value'), null=False, max_length=50)


class BusinessSchedule(models.Model):
    class Meta:
        db_table = 'business_schedule'

    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='schedule')
    weekday = models.CharField(_('weekday'), null=False, max_length=100, choices=Week.choices())
    time = models.CharField(_('time'), null=False, max_length=20)


class BusinessBranch(models.Model):
    class Meta:
        db_table = 'business_branches'

    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='branches')
    lat = models.DecimalField(_('latitude'), max_digits=9, decimal_places=6, null=False, blank=False,
                              default=DEFAULT_BRANCH_LATITUDE)
    lng = models.DecimalField(_('longitude'), max_digits=9, decimal_places=6, null=False, blank=False,
                              default=DEFAULT_BRANCH_LONGITUDE)
    address = models.CharField(_("address"), null=False, max_length=150)


class BusinessBanner(models.Model):
    class Meta:
        db_table = 'business_banners'

    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='banners')
    photo = models.ImageField(_('photo'), null=False, upload_to=banners_upload_to)
    text = models.CharField(_("text"), max_length=200, blank=True, null=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.photo_ = deepcopy(self.photo)

    def save(self, *args, **kwargs):
        if self.photo and self.photo != self.photo_:
            self.photo = compress_image(self.photo, business=True)
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        async_task(default_storage.delete, self.photo.name, task_name='remove banner image')
        super().delete(*args, **kwargs)


class BusinessStatistics(models.Model):
    """
    Storing business related stats like calls, messages, view and click count
    """
    VIEW = "view"
    CALL = "call"
    MESSAGE = "message"
    CLICK = "click"
    STATS_TYPE = (
        ("view", VIEW),
        ("call", CALL),
        ("message", MESSAGE),
        ("click", CLICK)
    )
    date = models.DateField(auto_now_add=True)
    stats_type = models.CharField(max_length=20, choices=STATS_TYPE)
    product = models.ForeignKey('product.Product', on_delete=models.CASCADE, null=True)

    class Meta:
        db_table = "business_statistics"


class BusinessCatalog(models.Model):
    class Meta:
        db_table = 'business_catalog'

    name = models.CharField(_("catalog_name"), max_length=150)
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name="business_catalog",
                                 verbose_name=_("business"))
    products = models.ManyToManyField(Product, related_name="catalog_product", verbose_name=_("product"))

    @property
    def product_count(self):
        return self.products.count()

class AddModal(models.Model):
    class Meta:
        db_table = 'add_modal'

    name = models.CharField(max_length=100)
    date = models.DateTimeField(null=True, blank=True)


class BusinessPeriod(models.Model):
    class Meta:
        db_table = "business_period"

    period_name = models.CharField(max_length=100, null=True, blank=True)
    end_date = models.DateTimeField(null=False, blank=False)

    def save(self, *args, **kwargs):
        business = Business.objects.all()
        users = User.objects.all()
        not_business = business.filter(is_not_demo=False)

        users.filter(id__in=not_business.values("user_id")).update(request_status=RequestStatuses.NOT_REQUESTED,
                                                                   remove_layout=None)
        not_business.update(deactivate_date=self.end_date)
        is_business = business.filter(is_not_demo=True)

        is_business.update(is_active=True, deactivate_date=self.end_date)
        users.filter(id__in=is_business.values("user_id")).update(request_status=RequestStatuses.SUCCESS)

        return super(BusinessPeriod, self).save(*args, **kwargs)
