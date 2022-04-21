import datetime

from django.db.models.signals import post_save, post_delete, pre_init, post_init
from django.dispatch import receiver

from product.models import Product
from users.settings import RequestStatuses
from .jobs import calculate_business_rating
from .models import Business


@receiver(post_save, sender=Product)
def post_save_product(sender, **kwargs):
    if hasattr(kwargs['instance'].user, 'business'):
        calculate_business_rating(kwargs['instance'].user.business)


@receiver(post_delete, sender=Product)
def post_delete_product(sender, **kwargs):
    if hasattr(kwargs['instance'].user, 'business'):
        calculate_business_rating(kwargs['instance'].user.business)


@receiver(post_delete, sender=Business)
def post_delete_business(sender, instance, **kwargs):
    instance.user.request_status = RequestStatuses.NOT_REQUESTED
    instance.user.save()

# @receiver(post_save, sender=Business)
# def post_business_create(sender, instance, created, **kwargs):
#     if instance.is_active == True:
#         instance.user.request_status = RequestStatuses.ACCEPTED
#     else:
#         instance.user.request_status = RequestStatuses.EXPIRED
#     instance.user.save()
