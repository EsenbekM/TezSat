import pytest
from django.urls import reverse
from rest_framework import status

from product.models import ProductReview, Claim, ClaimCategory
from product.settings import CurrencyType


@pytest.mark.django_db
def test_v2_list_view(api_client, product_factory):
    """
    Test product listing and product pagination
    """
    url = reverse('products-v2-list')
    for i in range(25):
        product_factory()

    response = api_client.get(url, format='json')
    results = response.data['results']

    assert response.status_code == 200
    assert 'key' in response.data
    assert len(results) == 20

    response2 = api_client.get(url + f"?key={response.data['key']}")

    assert response.status_code == 200
    assert response2.data['results'] != results


@pytest.mark.django_db
def test_v2_price_filter(api_client, product_factory):
    """
    Test product price filter and product ordering
    """
    url = reverse('products-v2-list')

    currency = CurrencyType.USD
    for i in range(20):
        product_factory(initial_price=i * 100, currency=currency)

    response = api_client.get(url + f"?price__gte=500&currency={currency}&ordering=price", format='json')
    assert response.status_code == 200

    result = response.data['results'][0]
    assert result['currency'] == currency
    assert float(result['initial_price']) >= 500.0


# @pytest.mark.django_db
# def test_v2_detail_view(api_client, product_factory):
#     """
#     Test product detail view
#     """
#     product = product_factory()
#
#     url = reverse('products-v2-detail', args=[product.id])
#
#     response = api_client.get(url, format='json')
#
#     assert response.status_code == 200


@pytest.mark.django_db
def test_v1_reviews_response_delete(api_client, product_factory, create_full_business):
    business = create_full_business
    product = product_factory(user=business.user)

    api_client.force_authenticate(user=business.user)

    review = ProductReview.objects.create(rating=3, review="ля ты криса", response='иди нафиг', user=business.user,
                                          product=product)
    url = reverse("product_reviews-response", args=[product.id, review.id])

    response = api_client.delete(url, format='json')

    product_review = ProductReview.objects.first()

    assert response.status_code == status.HTTP_200_OK
    assert product_review.response == None

@pytest.mark.django_db
def test_claim(api_client, product_factory, create_full_business):
    business = create_full_business

    api_client.force_authenticate(user=business.user)
    product = product_factory(user=business.user, title="Носки")

    claim_category = ClaimCategory.objects.create(claim_type="Другое")

    url = reverse('claim-list')
    response = api_client.get(url, format='json')

    assert response.status_code == 200
    assert len(response.data) == 1

    payload = {
        "type": claim_category.id,
        "message": "Продукт просрочен"
    }
    url = reverse("products-claim", args=[product.id])
    response = api_client.post(url, data=payload, format='json')
    assert response.status_code == 200
    assert response.data['product'] == product.id
    assert response.data['type'] == claim_category.id
    assert response.data['message'] == payload['message']

    response = api_client.post(url, data=payload, format='json')
    assert response.data['non_field_errors'][0]['code'] == 'unique'
