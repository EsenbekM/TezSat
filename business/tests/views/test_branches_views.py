import pytest
from rest_framework.reverse import reverse


@pytest.mark.django_db
@pytest.mark.parametrize(
    'lat, lng, address, status', [
        (None, None, None, 400),
        (43.677, None, None, 400),
        (None, 43.677, None, 400),
        (None, None, 'New place', 400),
        (43.677, 43.677, 'New place', 201),
    ]
)
def test_business_profile_create_branch(lat, lng, address, status, api_client, create_full_business):
    business = create_full_business
    url = reverse('branches-list')
    api_client.force_authenticate(user=business.user)

    payload = [
        {
            "lat": lat,
            "lng": lng,
            "address": address,
        },
        {
            "lat": lat,
            "lng": lng,
            "address": address,
        }
    ]

    response = api_client.post(url, payload, format='json')
    assert response.status_code == status


@pytest.mark.django_db
def test_business_profile_create_branch_fail(api_client, create_full_business):
    business = create_full_business
    url = reverse('branches-list')
    api_client.force_authenticate(user=business.user)

    payload = {
        "address": 'address',
    }
    response = api_client.post(url, payload, format='json')
    assert response.status_code == 400

    payload = {

    }
    response = api_client.post(url, payload, format='json')
    assert response.status_code == 400


@pytest.mark.django_db
def test_business_profile_create_branch_fail(api_client, create_full_business, business_factory, user_factory):
    business = create_full_business
    url = reverse('branches-list')
    payload = [
        {
            "lat": 90.11,
            "lng": 90.312,
            "address": 'address',
        }
    ]

    api_client.force_authenticate(user=business.user)
    response = api_client.post(url, payload, format='json')

    assert response.status_code == 201

    business2 = business_factory(is_active=True, user=user_factory())
    api_client.force_authenticate(user=business2.user)
    response2 = api_client.post(url, payload, format='json')

    assert response2.status_code == 201
    assert business.branches.count() == 2
    assert business2.branches.count() == 1


@pytest.mark.django_db
def test_business_profile_update_delete_branch(api_client, create_full_business, business_factory):
    business = create_full_business
    instance = business.branches.all().first()
    url = reverse('branches-detail', args=[instance.id])
    payload = {
        "lat": 90.11,
        "address": 'address',
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
