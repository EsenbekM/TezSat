from django.utils import timezone
from django_q.tasks import async_task

from .models import Notification, NotificationAction


def _update_date(**kwargs):
    notification, created = Notification.objects.get_or_create(**kwargs)
    if not created:
        notification.creation_date = timezone.now()
        notification.save()


def stared(sender, product):
    product.user.push_new_favorite(product.title, data={
        "product_id": str(product.id)
    })
    async_task(_update_date, sender=sender, receiver=product.user, product=product, action=NotificationAction.STARED,
               task_name='notification-stared')


def activated(product):
    product.user.push_active_product(product.title, data={"product_id": str(product.id)})
    async_task(_update_date, receiver=product.user, product=product, action=NotificationAction.ACTIVATED,
               task_name='notification-activated')


def blocked(product):
    product.user.push_blocked_product(product.title)
    async_task(_update_date, receiver=product.user, product=product, action=NotificationAction.BLOCKED,
               task_name='notification-blocked')
