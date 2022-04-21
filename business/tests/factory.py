import factory

from category.tests.factory import CategoryFactory
from users.tests.factory import UserFactory


class BusinessFactory(factory.django.DjangoModelFactory):
    """Business factory"""

    class Meta:
        model = 'business.Business'

    user = factory.SubFactory(UserFactory)
    category = factory.SubFactory(CategoryFactory)


class ContactFactory(factory.django.DjangoModelFactory):
    """Contact factory"""

    class Meta:
        model = 'business.BusinessContact'

    business = factory.SubFactory(BusinessFactory)


class ScheduleFactory(factory.django.DjangoModelFactory):
    """Schedule factory"""

    class Meta:
        model = 'business.BusinessSchedule'

    business = factory.SubFactory(BusinessFactory)


class BranchFactory(factory.django.DjangoModelFactory):
    """Branch factory"""

    class Meta:
        model = 'business.BusinessBranch'

    business = factory.SubFactory(BusinessFactory)


class BannerFactory(factory.django.DjangoModelFactory):
    """Banner factory"""

    class Meta:
        model = 'business.BusinessBanner'

    business = factory.SubFactory(BusinessFactory)
