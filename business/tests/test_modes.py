import pytest

from business import models


@pytest.mark.django_db
def test_create_business(business_factory):
    """
    Testing creation of business
    """
    name = "Deveem.io"
    business = business_factory(name=name)
    assert business.name == name
    assert models.Business.objects.count() == 1


@pytest.mark.django_db
def test_create_contact(contact_factory):
    """
    Testing creation of contact
    """
    value = "996777 777 777"
    contact_type = 'phone'
    contact = contact_factory(value=value, type=contact_type)

    assert contact.business
    assert contact.value == value
    assert contact.type == contact_type


@pytest.mark.django_db
def test_create_schedule(schedule_factory):
    """
    Testing creation of schedule
    """
    weekday = 'monday'
    time = '9-18'
    schedule = schedule_factory(weekday=weekday, time=time)

    assert schedule.business
    assert schedule.time == time
    assert schedule.weekday == weekday


@pytest.mark.django_db
def test_create_branch(branch_factory):
    """
    Testing creation of schedule
    """
    address = 'Цум, 4 этаж'
    branch = branch_factory(address=address)

    assert branch.address == address
    assert branch.business
    assert branch.lat
    assert branch.lng
