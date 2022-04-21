import pytest

from users.models import User


@pytest.mark.django_db
def test_user_create(user_factory):
    name = "User"
    user = user_factory(name=name)

    assert user.name == name
    assert user.location
    assert User.objects.count() == 1
