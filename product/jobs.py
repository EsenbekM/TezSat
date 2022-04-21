import os
from datetime import datetime, timedelta

import requests
from django.conf import settings
from django.db.models import F
from django.utils import timezone

from business.models import BusinessStatistics
from business.services import record_statistics
from product.models import (
    Product,
    Rate,
    CurrencyType,
    ProductState,
    ProductReview,
    Keyword,
)
from product.settings import PHOTO_TMP_DIR, PHOTO_TMP_LIFE_PERIOD
from tezsat.push_texts import PushBody, PushText, PushStatus
from users.models import User

BASE_DIR = settings.MEDIA_ROOT
FOLDER_FULL_PATH = os.path.join(BASE_DIR, PHOTO_TMP_DIR)


def remove_photos():
    for filename in os.listdir(FOLDER_FULL_PATH):
        file_path = os.path.join(FOLDER_FULL_PATH, filename)
        modification_date = os.stat(file_path).st_mtime
        date = datetime.fromtimestamp(modification_date)
        now = datetime.now(tz=date.tzinfo)
        if now - date >= PHOTO_TMP_LIFE_PERIOD:
            os.remove(file_path)


def update_show_count(products):
    ids = [p.id for p in products]
    Product.objects.filter(id__in=ids).update(show_count=F("show_count") + 1)
    record_statistics(product_ids=ids, stats_type=BusinessStatistics.VIEW)


def update_both_show_count(products):
    ids = [p.id for p in products]
    Product.objects.filter(id__in=ids).update(show_count=F("show_count") + 1)


def change_state(state, qs):
    notify_on_product_change(state, qs)


def notify_on_product_change(state, qs):
    for product in qs.iterator():
        product.state = state
        product.save()


def update_view_count(product):
    product.view_count = product.view_count + 1
    record_statistics(product_ids=[product.id], stats_type=BusinessStatistics.CLICK)
    product.save()


def update_both_view_count(product):
    Product.objects.filter(id__in=[product.id]).update(show_count=F("view_count") + 1)


def update_currency_rate():
    usd, _ = Rate.objects.get_or_create(currency=CurrencyType.USD)
    try:
        r = requests.get("https://valuta.kg/api/rate/nbkr.json", timeout=10)
    except requests.RequestException:
        return
    if r.status_code != 200:
        return
    data = r.json()
    if data["error"]:
        return
    rate, direction = data["data"]["rates"]["USD"]
    usd.rate = rate
    usd.save()


def update_prices():
    usd = Rate.objects.get(currency=CurrencyType.USD)
    iterator = Product.objects.filter(
        state__in=[ProductState.ACTIVE, ProductState.ON_REVIEW]
    ).iterator()
    products = []
    for product in iterator:
        if product.currency == CurrencyType.USD:
            product.price_usd = product.initial_price
            product.price_kgs = product.initial_price * usd.rate
        else:
            product.price_kgs = product.initial_price
            product.price_usd = product.initial_price / usd.rate
        products.append(product)

    Product.objects.bulk_update(products, ["price_kgs", "price_usd"], batch_size=1000)


def calculate_product_rating(product):
    reviews = ProductReview.objects.filter(product_id=product.id).all()
    # deprecated // 4 points by reviews and 1 point by like/dislike
    # https://math.stackexchange.com/questions/1642158/number-of-likes-and-dislikes-to-star-rating-system

    review_rating = (
        sum([review.rating for review in reviews]) / len(reviews)
        if len(reviews) != 0
        else None
    )
    product.rating = review_rating
    product.save()


def create_search_keyword(keyword):
    Keyword.objects.create(keyword=keyword, is_search=True)


def update_call_count(product):
    product.call_count += 1
    record_statistics(product_ids=[product.id], stats_type=BusinessStatistics.CALL)
    product.save()


def notify_not_upvoted_product():
    upvote_date = timezone.now() - timedelta(days=2)
    creation_date = timezone.now() - timedelta(days=10)
    users = (
        User.objects.filter(
            products__creation_date__gte=creation_date,
            products__upvote_date__lte=upvote_date,
            products__state=ProductState.ACTIVE,
            business__isnull=True,
        )
            .distinct("email", "fcm_id")
            .all()
    )
    for user in users:
        try:
            user.send_message(
                title=PushText.upvote_reminder[user.language],
                body=PushBody.upvote_reminder[user.language],
                status=PushStatus.UPVOTE,
            )
        except Exception:
            pass


def regular_product_upvote():
    upvote_threshold = datetime.now() - timedelta(days=2)
    product = (
        Product.objects.filter(upvote_date__lte=upvote_threshold)
            .order_by("-upvote_date")
            .first()
    )
    product.upvote_date = datetime.now()
    product.save()
