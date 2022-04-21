import pytest
from pytest_factoryboy import register

from category.tests.factory import CategoryFactory
from product.tests.factory import ProductFactory
from users.tests.factory import UserFactory
from .factory import BusinessFactory, ContactFactory, ScheduleFactory, BranchFactory, BannerFactory

register(UserFactory)
register(CategoryFactory)
register(BusinessFactory)
register(ContactFactory)
register(ScheduleFactory)
register(BranchFactory)
register(ProductFactory)


@pytest.fixture
def create_full_business():
    business = BusinessFactory(is_active=True, user=UserFactory())
    ContactFactory(business=business)
    ScheduleFactory(business=business)
    BranchFactory(business=business)
    BannerFactory(business=business)
    return business


@pytest.fixture
def api_client(admin_user):
    from rest_framework.test import APIClient
    return APIClient()
