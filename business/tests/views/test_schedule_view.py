import pytest
from rest_framework.reverse import reverse

from business.models import BusinessSchedule


@pytest.mark.django_db
@pytest.mark.parametrize(
    'weekday, time, status', [
        (None, None, 400),
        (None, 'today', 400),
        ('monday', None, 400),
        ('not monday', 'today', 400),
        ('monday', 'today', 201),
    ]
)
def test_business_profile_create_schedule(weekday, time, status, api_client, create_full_business):
    business = create_full_business
    url = reverse('schedule-list')
    api_client.force_authenticate(user=business.user)

    payload = [
        {
            "weekday": weekday,
            "time": time,
        },
    ]

    response = api_client.post(url, payload, format='json')
    assert response.status_code == status


@pytest.mark.django_db
def test_business_profile_create_schedule_fail(api_client, create_full_business):
    business = create_full_business
    url = reverse('schedule-list')
    api_client.force_authenticate(user=business.user)

    payload = {
        "time": 'tomorrow',
    }
    response = api_client.post(url, payload, format='json')
    assert response.status_code == 400

    payload = {

    }
    response = api_client.post(url, payload, format='json')
    assert response.status_code == 400


@pytest.mark.django_db
def test_business_profile_create_schedule_fail(api_client, create_full_business, business_factory, user_factory):
    business = create_full_business
    url = reverse('schedule-list')
    payload = [
        {
            "time": 'today',
            "weekday": 'monday'
        }
    ]

    api_client.force_authenticate(user=business.user)
    response = api_client.post(url, payload, format='json')

    assert response.status_code == 201

    business2 = business_factory(is_active=True, user=user_factory())
    api_client.force_authenticate(user=business2.user)
    response2 = api_client.post(url, payload, format='json')

    assert response2.status_code == 201
    assert business.schedule.count() == 2
    assert business2.schedule.count() == 1


@pytest.mark.django_db
def test_business_profile_update_delete_schedule(api_client, create_full_business, business_factory):
    business = create_full_business
    instance = business.schedule.all().first()
    url = reverse('schedule-detail', args=[instance.id])
    payload = {
        "weekday": 'monday',
        "time": 'today',
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


@pytest.mark.djano_db
def test_business_schedule_duplicate_creation(api_client, create_full_business):
    business = create_full_business
    count = BusinessSchedule.objects.count()
    payload = [
        {
            "weekday": 'monday',
            "time": 'today',
        },
        {
            "weekday": 'monday',
            "time": 'tomorrow',
        },
    ]
    api_client.force_authenticate(user=business.user)
    url = reverse('schedule-list')
    api_client.post(url, payload, format='json')
    count2 = BusinessSchedule.objects.count()
    assert BusinessSchedule.objects.last().time == "tomorrow"
    assert count + 1 == count2
