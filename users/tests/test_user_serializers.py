import pytest

from users import serializers


# TODO: Add test for business accounts as long as they added

@pytest.mark.django_db
def test_public_serializers(user_factory):
    user = user_factory()
    serializer = serializers.PublicUserSerializer(user)
    assert serializer.data["is_business"] == False
    assert serializer.data['business'] is None


@pytest.mark.django_db
def test_private_serializers(user_factory):
    user = user_factory()
    serializer = serializers.UserSerializer(user)
    assert serializer.data["is_business"] == False
    assert serializer.data['business'] is None
    # assert serializer.data['fcm_id']
    # assert serializer.data['firebase_uid']
