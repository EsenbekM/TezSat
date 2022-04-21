import factory
from faker import Factory as FakerFactory

faker = FakerFactory.create()


class LocationFactory(factory.django.DjangoModelFactory):
    """Location factory"""

    class Meta:
        model = 'location.Location'


class UserFactory(factory.django.DjangoModelFactory):
    """User factory"""

    class Meta:
        model = 'users.User'

    location = factory.SubFactory(LocationFactory)
