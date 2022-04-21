import pytest
from pytest_factoryboy import register

from business.tests.factory import BusinessFactory, ContactFactory, ScheduleFactory, BranchFactory, BannerFactory
from users.tests.factory import UserFactory
from .factory import ProductFactory

register(ProductFactory)
register(UserFactory)


@pytest.fixture
def api_client(admin_user):
    from rest_framework.test import APIClient
    return APIClient()

@pytest.fixture
def create_full_business():
    business = BusinessFactory(is_active=True, user=UserFactory())
    ContactFactory(business=business)
    ScheduleFactory(business=business)
    BranchFactory(business=business)
    BannerFactory(business=business)
    return business