import random
import pytest
from django.urls import reverse
from rest_framework import status

from product.models import Rate
from product.settings import CurrencyType


@pytest.mark.django_db
def test_discounts_get(api_client, create_full_business, product_factory):
    user = create_full_business.user
    url = reverse("discounts-list", args=[user.id])
    api_client.force_authenticate(user=user)
    [product_factory(user=user, discount=i * 50, discount_price_kgs=i * 20, discount_price_usd=10.00) for i in range(5)]
    response = api_client.get(url, format='json')
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 5


@pytest.mark.django_db
def test_last_discount(api_client, create_full_business, product_factory):
    user = create_full_business.user
    url = reverse("discounts-last-discounts", args=[user.id])
    api_client.force_authenticate(user=user)
    [product_factory(user=user, discount=i * 50, discount_price_kgs=i * 20, discount_price_usd=10.00) for i in
     range(10)]
    response = api_client.get(url, format="json")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 4

@pytest.mark.django_db
def test_create_discount(api_client, create_full_business, product_factory):
    user = create_full_business.user
    product = product_factory(user=user, discount=0)
    url = reverse("products-detail", args=[product.id])
    api_client.force_authenticate(user=user)
    response = api_client.get(url, format="json")
    assert response.status_code == status.HTTP_200_OK
    assert response.data["discount_price_kgs"] == None
    assert response.data["discount_price_usd"] == None


@pytest.mark.django_db
def test_discounts_post(api_client, product_factory, create_full_business):
    user = create_full_business.user
    url = reverse("discounts-list", args=[user.id])
    api_client.force_authenticate(user=user)
    products = [product_factory(price_kgs=i * 100, price_usd=i * 100, user=user).id for i in
                range(5)]
    payload = {
        "products": products,
        "discount": 0
    }
    response = api_client.post(url, payload, format='json')
    assert response.data["message"] == "discount applied"
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_discounts_patch(api_client, product_factory, create_full_business):
    api_client.force_authenticate(user=create_full_business.user)
    product = product_factory(currency='USD', user=create_full_business.user)
    rate = Rate.objects.filter(rate="1.00").update(rate="84.66")
    payload = {
        "discount": 0,
    }
    url = reverse("personal_products-detail", args=[product.id])
    response = api_client.patch(url, payload, format='json')
    assert response.data['discount_price_kgs'] == None
    assert response.data["discount_price_usd"] == None
    # assert response.data['discount_price_kgs'] == '8466.00'
    # assert response.data["discount_price_usd"] == '100.00'
