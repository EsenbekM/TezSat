import pytest

from business import serializers


@pytest.mark.django_db
def test_business_serializer(business_factory):
    """
    Testing business serializer without contacts, schedule, contacts
    """
    business = business_factory()
    serializer = serializers.ShortBusinessSerializer(branch=business)

    assert serializer.data['name']
    assert serializer.data['description']
    assert serializer.data['creation_date']
    assert serializer.data['category']
    assert serializer.data['rating']
    assert serializer.data['product_limit']


@pytest.mark.django_db
def test_business_serializer(business_factory, contact_factory, schedule_factory, branch_factory):
    """
    Testing business serializer with contacts, schedule, contacts
    """
    business = business_factory()
    contacts = serializers.BusinessContactSerializer([contact_factory(business=business)], many=True)
    schedule = serializers.BusinessScheduleSerializer([schedule_factory(business=business)], many=True)
    # branches = serializers.BusinessBranchSerializer([branch_factory(business=business)], many=True)

    serializer = serializers.BusinessSerializer(business)

    assert serializer.data['contacts'] == contacts.data
    assert serializer.data['schedule'] == schedule.data
    # assert serializer.data['branches'] == branches.data
