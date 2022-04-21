import pytest
from rest_framework.reverse import reverse


@pytest.mark.django_db
def test_business_profile_create_banners_fail(api_client, create_full_business):
    business = create_full_business
    url = reverse('banners-list')
    api_client.force_authenticate(user=business.user)

    payload = {
        "photo": 'some text',
    }
    response = api_client.post(url, payload, format='json')
    assert response.status_code == 400

    payload = {

    }
    response = api_client.post(url, payload, format='json')
    assert response.status_code == 400


@pytest.mark.django_db
def test_business_profile_update_delete_banner(api_client, create_full_business, business_factory):
    business = create_full_business
    instance = business.banners.all().first()
    url = reverse('banners-detail', args=[instance.id])
    payload = {
        "text": 'some text',
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
