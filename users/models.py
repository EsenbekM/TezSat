from copy import deepcopy

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.core.validators import validate_email
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_q.tasks import async_task
from firebase_admin import messaging, firestore
from phonenumber_field.modelfields import PhoneNumberField

from tezsat.push_texts import PushBody
from tezsat.utils import get_filename, compress_image
from .settings import PROFILE_UPLOAD_DIR, Lang, Platforms, SignInMethods, PushText, manager_apps, manager_permissions, \
    RequestStatuses


class UserManager(BaseUserManager):
    def create_superuser(self, email, password):
        user = self.model(email=self.normalize_email(email))
        user.set_password(password)
        user.is_superuser = True
        user.save()
        return user

    def create_user(self, email, password):
        user = self.model(email=self.normalize_email(email))
        user.set_password(password)
        user.save()
        return user

    def get_by_natural_key(self, username):
        case_insensitive_username_field = '{}__iexact'.format(self.model.USERNAME_FIELD)
        return self.get(**{case_insensitive_username_field: username})


def upload_profile_photo_to(instance, filename):
    new_filename = get_filename(filename)
    return f'{PROFILE_UPLOAD_DIR}/{new_filename}'


class User(AbstractBaseUser):
    class Meta:
        db_table = 'user'

    USERNAME_FIELD = 'email'

    objects = UserManager()

    name = models.CharField(_('name'), max_length=50, null=True, blank=True)
    email = models.EmailField(_('email address'), unique=True, null=True, blank=True, validators=(validate_email,))
    phone = PhoneNumberField(_('phone number'), unique=True, null=True, blank=True)
    date_joined = models.DateTimeField(_('registration date'), auto_now_add=True)
    is_active = models.BooleanField(_('is active'), default=True)
    is_superuser = models.BooleanField(_('is superuser'), default=False)
    is_manager = models.BooleanField(_('is manager'), default=False)
    password = models.CharField(_('password'), max_length=128, null=True, blank=True)
    photo = models.ImageField(_('photo'), upload_to=PROFILE_UPLOAD_DIR, null=True, blank=True)
    language = models.CharField(_('language'), max_length=10, choices=Lang.choices(), default=Lang.KY, null=True,
                                blank=True)
    platform = models.CharField(_('platform'), max_length=20, choices=Platforms.choices(), null=True, blank=True)

    firebase_uid = models.CharField(_('firebase user id'), max_length=50, null=True, blank=True)
    facebook_uid = models.CharField(_('firebase user id'), max_length=50, null=True, blank=False, unique=True)
    fcm_id = models.CharField(_('firebase cloud messaging id'), max_length=200, null=True, blank=True)

    location = models.ForeignKey('location.Location', on_delete=models.PROTECT, null=True, blank=True)

    favorites = models.ManyToManyField('product.Product', related_name='favorites')
    likes = models.ManyToManyField('product.Product', related_name='likes')

    sign_in_method = models.CharField('sign in method', max_length=50, choices=SignInMethods.choices(),
                                      default=SignInMethods.credentials)
    provider = models.CharField('sign_in_provider', max_length=50, default='phone')
    last_active = models.DateTimeField(_('last active date'), null=True, blank=True)
    categories = models.ManyToManyField('category.Category', related_name='users')
    request_status = models.CharField(
        _("business request status"), max_length=50,
        choices=RequestStatuses.choices(), default=RequestStatuses.NOT_REQUESTED
    )
    balance = models.IntegerField(_('Balance'), default=0, blank=True)
    remove_layout = models.DateField(_('remove layout'), null=True, blank=True)

    def update_balance(self, balance, status: str):
        if status == 'plus':
            self.balance += balance
        else:
            self.balance -= balance
        self.save()
        return self.balance

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.photo_ = deepcopy(self.photo)

    def __str__(self):
        title = self.name or self.email or self.phone
        return str(title)

    def save(self, *args, **kwargs):
        if self.photo and self.photo != self.photo_:
            self.photo = compress_image(self.photo, is_medium_thumbnail=True, quality=80)
        super().save(*args, **kwargs)

    @property
    def is_staff(self):
        return self.is_superuser or self.is_manager

    def has_module_perms(self, module, *args, **kwargs):
        if not self.is_active:
            return False
        if self.is_superuser:
            return True
        if self.is_manager:
            return module in manager_apps
        return False

    def has_perm(self, permission, *args, **kwargs):
        if not self.is_active:
            return False
        if self.is_superuser:
            return True
        module, permission = permission.split('.')
        permission = permission.split('_')[0]
        if permission in manager_permissions.get(module, {}):
            return True
        return False

    def send_message(self, title, body=None, data=None, status='default'):
        if not self.fcm_id:
            print('fcm_id is empty')
            return
        if data is None:
            data = {}
        title = title.strip()
        if title == 'Доступно новое обновление!' or title == 'Тиркемени жаңылаңыз!':
            status = 'update'
        data['title'] = title
        data['message'] = body if body is not None else ''
        data['status'] = status

        if self.platform == Platforms.android:
            android_notification = messaging.AndroidNotification(title=data["title"], body=data["message"], default_sound=True, sound="default")
            android_conf = messaging.AndroidConfig(notification=android_notification, data=data)
            message = messaging.Message(data=data, token=self.fcm_id, android=android_conf)
        else:
            notification = messaging.Notification(title=title, body=body)
            message = messaging.Message(data=data, token=self.fcm_id, notification=notification,
                                        apns=messaging.APNSConfig(
                                            payload=messaging.APNSPayload(aps=messaging.Aps(sound='default'))))
        messaging.send(message)

    def push_new_message(self, sender, message, data=None):
        async_task(self.send_message, PushText.new_message[self.language], message, data,
                   task_name='user-push-new-message')

    def push_new_favorite(self, message=None, data=None):
        async_task(self.send_message, PushText.new_favorite[self.language], message, data,
                   task_name='user-push-new-favorite')

    def push_active_product(self, message=None, data=None):
        async_task(self.send_message, PushText.product_activated[self.language], message, data,
                   task_name='user-push-product-activated')

    def push_blocked_product(self, message=None):
        async_task(self.send_message, PushText.product_blocked[self.language], message,
                   task_name='user-push-product-blocked')

    def push_business_activated(self, message=None):
        async_task(self.send_message, PushText.business_activated[self.language], message, status='profile',
                   task_name='user-push-business-activated')

    def push_new_comment(self, message=None, title=None, data=None):
        async_task(self.send_message, title, message, data,
                   task_name='user-push-new-comment')

    def upvote_reminder(self, message=None):
        async_task(self.send_message, PushText.upvote_reminder[self.language], message,
                   task_name='user-upvote-reminder')
    def push_denied(self, message=None):
        async_task(self.send_message, title=PushText.denied_title, body=PushBody.denied_body[self.language], status='profile',
                   task_name='user-denied-business')

class SMSCode(models.Model):
    class Meta:
        db_table = 'sms_code'

    code = models.CharField(_('code'), max_length=10)
    phone = models.CharField(_('phone'), max_length=15)
