import pytest
from rest_framework.reverse import reverse


@pytest.mark.django_db
@pytest.mark.parametrize(
    'type, value, status', [
        (None, None, 400),
        ('phone', None, 400),
        (None, '+9962202020202', 400),
        ('not phone', '+9962202020202', 400),
        ('phone', '+9962202020202', 201),
    ]
)
def test_business_profile_create_contact(type, value, status, api_client, create_full_business):
    business = create_full_business
    url = reverse('contacts-list')
    api_client.force_authenticate(user=business.user)

    payload = [
        {
            "type": type,
            "value": value,
        },
        {
            "type": type,
            "value": value
        }
    ]

    response = api_client.post(url, payload, format='json')
    assert response.status_code == status


@pytest.mark.django_db
def test_business_profile_create_contact_fail(api_client, create_full_business):
    business = create_full_business
    url = reverse('contacts-list')
    api_client.force_authenticate(user=business.user)

    payload = [
        {
            "value": '+89912341',
        }
    ]
    response = api_client.post(url, payload, format='json')
    assert response.status_code == 400

    payload = {
    }
    response = api_client.post(url, payload, format='json')
    assert response.status_code == 400


@pytest.mark.django_db
def test_business_profile_create_contact_two_users(api_client, create_full_business, business_factory, user_factory):
    business = create_full_business
    url = reverse('contacts-list')
    payload = [
        {
            "type": 'phone',
            "value": '+997242334'
        }
    ]

    api_client.force_authenticate(user=business.user)
    response = api_client.post(url, payload, format='json')

    assert response.status_code == 201

    business2 = business_factory(is_active=True, user=user_factory())
    api_client.force_authenticate(user=business2.user)
    response2 = api_client.post(url, payload, format='json')

    assert response2.status_code == 201
    assert business.contacts.count() == 2
    assert business2.contacts.count() == 1


@pytest.mark.django_db
def test_business_profile_update_delete_contact(api_client, create_full_business, business_factory):
    business = create_full_business
    instance = business.contacts.all().first()
    url = reverse('contacts-detail', args=[instance.id])
    payload = {
        "type": 'phone',
        "value": '+998989239',
    }
    api_client.force_authenticate(user=business.user)
    response = api_client.patch(url, payload, format='json')
    assert response.status_code == 200

    business2 = business_factory(is_active=True)
    api_client.force_authenticate(user=business2.user)

    response2 = api_client.patch(url, payload, format='json')
    assert response2.status_code == 404

    response3 = api_client.delete(url, format='json')
    assert response3.status_code == 404
