import random

from django.utils import timezone
from notification.models import Notification
from notification.settings import NotificationAction
from product.models import Product, ProductState
from tezsat.push_texts import PushBody, PushText
from users.settings import RequestStatuses
from .models import Business


def calculate_business_rating(business):
    products = Product.objects.filter(
        user=business.user, state=ProductState.ACTIVE, rating__isnull=False
    )
    if len(products) != 0:
        business.rating = (
            sum([product.rating for product in products]) / len(products)
            if len(products) != 0
            else None
        )
        business.save()


def auto_upvote():
    businesses = Business.objects.filter(is_active=True).select_related("user")
    products = Product.objects.filter(state=ProductState.ACTIVE).exclude(user__business__is_active=True)

    for business in businesses:
        if business.upvote_count != 0:
            now = timezone.now()
            upvote_period = now - timezone.timedelta(
                hours=(24 / business.upvote_count + 10)
            )
            business_products = business.user.products.filter(
                state=ProductState.ACTIVE, upvote_date__lte=upvote_period
            ).order_by("upvote_date")
            if not business_products:
                continue
            business_product = business_products.first()

            excluded = business_products.values_list("id", flat=True)
            products = products.exclude(id__in=excluded).values_list('id', flat=True)
            random_id = random.choice(products)
            random_product = Product.objects.filter(id=random_id).first()
            business_product.upvote_date = now
            upvote_products = [business_product]
            #
            random_product.upvote_date = now
            upvote_products.append(random_product)
            Product.objects.bulk_update(
                upvote_products, ["upvote_date"]
            )


def denied_push(queryset):
    for i in queryset:
        i.user.push_denied()
        i.denied = True
        i.save()
        i.user.request_status = RequestStatuses.EXPIRED_NONE
        i.user.save()
        Notification.objects.create(receiver=i.user, title_ky=PushText.denied_title, title_ru=PushText.denied_title,
                                    description_ky=PushBody.denied_body,
                                    description_ru=PushBody.denied_body,
                                    action=NotificationAction.PAYMENT)
