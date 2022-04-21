import datetime
import random

import pytest
from django.urls import reverse

from business.models import Business, BusinessSchedule, BusinessCatalog
from business.settings import Week
from category.models import Category
from product.models import ProductReview, Product
from users.settings import RequestStatuses


@pytest.mark.django_db
def test_business_profile_view(api_client, create_full_business, product_factory, user_factory):
    # test unread_reviews_count and business_catalogs
    business = create_full_business
    url = reverse('business-profile')
    api_client.force_authenticate(user=business.user)
    product = product_factory(user=business.user)
    for i in range(5):
        user = user_factory(name=f"user {i}")
        is_read = False
        if i % 2 != 0:
            is_read = True
        ProductReview.objects.create(rating=i, review=f"норм товар {i}", user=user, product=product, is_read=is_read)
        catalog = BusinessCatalog.objects.create(name=f"catalog {i}", business=business)
        catalog.products.add(product_factory(user=business.user))
    response = api_client.get(url, format='json')
    assert response.status_code == 200
    assert response.data['unread_reviews_count'] == 2
    assert len(response.data['catalogs']) == 5


@pytest.mark.django_db
def test_business_profile_update(api_client, create_full_business):
    business = create_full_business
    url = reverse('business-profile')
    api_client.force_authenticate(user=business.user)

    payload = {
        "name": "Deveem 2",
        "description": "New description",
        "category": business.category.id
    }
    response = api_client.patch(url, payload, format='json')
    # Category is now object, not a single id
    payload.pop('category')
    for key, value in payload.items():
        assert response.data[key] == value


@pytest.mark.django_db
def test_business_request(admin_user, api_client, category_factory):
    category = category_factory()
    api_client.force_authenticate(admin_user)
    url = reverse('requests-list')
    payload = {
        "name": "Test business",
        "message": "Want business very hard!",
        "category": category.id
    }
    assert admin_user.request_status == RequestStatuses.NOT_REQUESTED
    response = api_client.post(path=url, data=payload, format='json')

    admin_user.refresh_from_db()
    assert admin_user.request_status == RequestStatuses.ON_REVIEW


@pytest.mark.djang_db
def test_status_update_on_activation(admin_user, api_client, category_factory):
    category = category_factory()
    api_client.force_authenticate(admin_user)
    url = reverse('requests-list')
    payload = {
        "name": "Test business",
        "message": "Want business very hard!",
        "category": category.id
    }
    response = api_client.post(path=url, data=payload, format='json')

    business = Business.objects.get(pk=response.data['id'])
    business.is_active = True
    business.save()

    assert business.user.request_status == RequestStatuses.ACCEPTED


@pytest.mark.djang_db
def test_status_update_on_first_activation(api_client, create_full_business):
    business = create_full_business
    business.user.request_status = RequestStatuses.ACCEPTED
    business.user.save()
    api_client.force_authenticate(business.user)
    url = reverse('business-profile')
    response = api_client.get(path=url, format='json')

    business.user.refresh_from_db()
    assert response.status_code == 200
    assert business.user.request_status == RequestStatuses.SUCCESS

    business.user.refresh_from_db()
    response = api_client.get(path=url, format='json')
    assert response.status_code == 200
    assert business.user.request_status == RequestStatuses.SUCCESS


@pytest.mark.django_db
def test_week_order(api_client, create_full_business, product_factory):
    business = create_full_business
    api_client.force_authenticate(business.user)
    product_factory(user=business.user)
    wrong_answer = [Week.friday, Week.sunday, Week.monday, Week.tuesday]
    correct_answer = [Week.monday, Week.tuesday, Week.friday, Week.sunday]
    for i in wrong_answer:
        BusinessSchedule.objects.create(business=business, weekday=i, time=random.randint(1, 24))
    url = reverse('business-profile')
    response = api_client.get(path=url, format='json')
    assert response.status_code == 200
    for i in range(4):
        assert response.data['schedule'][i]['weekday'] == correct_answer[i]


@pytest.mark.djang_db
def test_reviews_count(api_client, product_factory, create_full_business):
    business = create_full_business
    api_client.force_authenticate(business.user)
    product = product_factory(user=business.user)
    user1 = create_full_business
    ProductReview.objects.create(rating=4, review="ля ты криса", response="иди нафиг", user=user1.user, product=product)
    url = reverse('business-profile')
    response = api_client.get(path=url, format='json')
    assert response.status_code == 200
    assert response.data['reviews_count'] == 1


@pytest.mark.djang_db
def test_unread_reviews(api_client, product_factory, create_full_business, user_factory):
    business = create_full_business
    api_client.force_authenticate(business.user)
    product = product_factory(user=business.user)
    for i in range(5):
        user = user_factory(name=f"user {i}")
        ProductReview.objects.create(rating=i, review=f"норм товар {i}", user=user, product=product)

    url = reverse('reviews-list')
    response = api_client.get(path=url, format='json')
    assert response.status_code == 200
    assert len(response.data) == 5

    url2 = reverse('reviews-detail', args=[1])
    response2 = api_client.patch(path=url2, format='json')
    assert response2.status_code == 200

    response = api_client.get(path=url, format='json')
    assert response.status_code == 200
    assert len(response.data) == 0


@pytest.mark.django_db
def test_delivery(api_client, product_factory, create_full_business):
    business = create_full_business
    api_client.force_authenticate(business.user)
    url = reverse('business-profile')
    response = api_client.get(path=url, format='json')
    assert response.data['delivery'] == None
    payload = {
        'delivery': 100
    }
    response = api_client.patch(path=url, data=payload, format='json')
    assert response.status_code == 200
    assert response.data['delivery'] == 100


@pytest.mark.django_db
def test_change_catalog_name(api_client, product_factory, create_full_business):
    business = create_full_business
    api_client.force_authenticate(user=business.user)
    product = product_factory(user=business.user)
    catalog = BusinessCatalog.objects.create(name='car', business=business)
    catalog.products.add(product)
    url = reverse('catalog-detail', args=[business.id, catalog.id])
    response = api_client.get(path=url, format='json')
    assert response.data['name'] == 'car'

    payload = {
        'name': 'Home'
    }
    response = api_client.patch(path=url, data=payload, format='json')
    assert response.status_code == 200
    assert response.data['name'] == 'Home'

@pytest.mark.django_db
def test_removing_product_from_the_catalog(api_client, product_factory, create_full_business):
    business = create_full_business
    api_client.force_authenticate(user=business.user)
    products = [product_factory(user=business.user) for i in range(10)]

    catalog = BusinessCatalog.objects.create(name='car', business=business)
    catalog.products.add(*products)
    url = reverse('catalog-detail', args=[business.id, catalog.id])

    payload = {
        'products': [products[0].id, products[-1].id]
    }
    assert len(Product.objects.all()) == 10
    response = api_client.delete(path=url, data=payload, format='json')
    assert response.status_code == 204
    assert len(Product.objects.all()) == 8

@pytest.mark.django_db
def test_demo_business(api_client, create_full_business, user_factory):
    user = user_factory()

    api_client.force_authenticate(user=user)
    category = Category.objects.create(title_ru='car', title_ky='car')
    payload = {
        "name": "imanji",
        "category": category.id
    }
    # запрос для активации бизнеса
    url = reverse('requests-list')  # requests-list

    response = api_client.post(path=url, data=payload, format='json')
    assert response.status_code == 201

    # теперь у юзера статус ON_REVIEW
    assert user.request_status == RequestStatuses.ON_REVIEW
    # делаем юзера бизнесом
    business = Business.objects.filter(is_active=False).first()
    business.is_active = True
    business.save()

    # будем отпралять запрос уже от бизнеса
    api_client.force_authenticate(business.user)
    url = reverse("business-profile")  # business-profile

    response = api_client.get(path=url, format='json')
    assert response.status_code == 200
    assert response.data['time_left'] == 59

    date = business.creation_date + datetime.timedelta(weeks=8, days=4)
    assert business.deactivate_date == date

    # сделаем так будто у бизнеса срок уже просрочен
    business.deactivate_date = datetime.datetime.now()
    url = reverse("business-profile")
    response = api_client.get(path=url, format='json')
    assert response.data['time_left'] == 0
    assert business.user.request_status == RequestStatuses.EXPIRED
    assert business.is_active == False


