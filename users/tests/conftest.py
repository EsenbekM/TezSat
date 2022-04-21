from pytest_factoryboy import register

from .factory import UserFactory, LocationFactory

register(LocationFactory)
register(UserFactory)
