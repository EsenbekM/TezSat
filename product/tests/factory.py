import random

import factory
from faker import Generator, Factory as FakerFactory

from business.tests.factory import CategoryFactory
from product.settings import CurrencyType
from users.tests.factory import UserFactory, LocationFactory

faker = FakerFactory()
generator = Generator()


class ProductFactory(factory.django.DjangoModelFactory):
    """Product Factory"""

    class Meta:
        model = 'product.Product'

    user = factory.SubFactory(UserFactory)
    category = factory.SubFactory(CategoryFactory)
    location = factory.SubFactory(LocationFactory)
    initial_price = 100

class TariffFactory(factory.django.DjangoModelFactory):
    """Tariff Factory"""

    class Meta:
        model = 'payment.Tariff'
    period = random.randint(1, 6)

    amount = random.randint(100, 1000)
    currency = CurrencyType.KGS
    name_ru = 'tariff %s' % period
    name_kgz = 'tariff %s' % period
    period = period