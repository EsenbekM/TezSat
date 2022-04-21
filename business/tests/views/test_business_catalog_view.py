import pytest
from django.urls import reverse
from rest_framework import status

from business.models import BusinessCatalog


@pytest.mark.django_db
def test_business_catalog_create(api_client, create_full_business):
    business = create_full_business
    url = reverse('catalog-list', args=[business.id])
    api_client.force_authenticate(user=business.user)
    response = api_client.post(url, data={"name": "tovar"}, format='json')
    assert response.status_code == 201


@pytest.mark.django_db
def test_business_catalog_product_add(api_client, create_full_business, product_factory):
    business = create_full_business
    products = [product_factory().id for i in range(6)]
    api_client.force_authenticate(user=business.user)
    business_catalog = BusinessCatalog.objects.create(name="машины", business=business)
    url = reverse('catalog-detail', args=[business.id, business_catalog.id])
    payload = {
        "products": products
    }
    response = api_client.patch(url, payload, format="json")
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_business_catalog_get(api_client, create_full_business, product_factory):
    business = create_full_business
    api_client.force_authenticate(user=business.user)
    business_catalog = BusinessCatalog.objects.create(name="машины", business=business)
    products = [product_factory().id for i in range(6)]
    business_catalog.products.set(products)
    url = reverse('catalog-list', args=[business.id])
    response = api_client.get(url, format="json")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data[0]['products']) == 4


@pytest.mark.django_db
def test_business_catalog_patch(api_client, create_full_business, product_factory):
    business = create_full_business
    api_client.force_authenticate(user=business.user)
    business_catalog = BusinessCatalog.objects.create(name="машины", business=business)
    products = [product_factory().id for i in range(3)]
    url = reverse('catalog-detail', args=[business.id, business_catalog.id])
    payload = {
        "products": products
    }
    response = api_client.patch(url, payload, format="json")
    assert len(response.data["products"]) == 3
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_business_catalog_get_unauthorized(api_client, create_full_business, product_factory):
    business = create_full_business
    business_catalog = BusinessCatalog.objects.create(name="машины", business=business)
    products = [product_factory().id for i in range(5)]
    business_catalog.products.set(products)
    url = reverse('catalog-detail', args=[business.id, business_catalog.id])
    response = api_client.get(url, format="json")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["id"] == business_catalog.id
    assert len(response.data["products"]) == 5


@pytest.mark.django_db
def test_business_catalog_get_list_unauthorized(api_client, create_full_business, product_factory):
    business = create_full_business
    business_catalog = BusinessCatalog.objects.create(name="машины", business=business)
    products = [product_factory().id for i in range(5)]
    business_catalog.products.set(products)
    url = reverse('catalog-list', args=[business.id])
    response = api_client.get(url, format="json")

    assert response.status_code == status.HTTP_200_OK
