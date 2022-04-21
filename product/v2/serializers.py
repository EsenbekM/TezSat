from decouple import config
from django.conf import settings
from rest_framework import serializers as s


class AbsolutePathImageField(s.URLField):

    def to_representation(self, value):
        s3_url = config('AWS_S3_CUSTOM_DOMAIN', None)
        if s3_url:
            media_host = f"https://{s3_url}"
            return f"{media_host}/media/{value}"

        return self.context['request'].build_absolute_uri(f"{settings.MEDIA_URL}{value}")


# TODO: Refactor to dynamic serializers
class SuggestionsSerializer(s.Serializer):
    id = s.IntegerField()
    title = s.CharField()
    is_category = s.BooleanField()


class V2ParameterSerializer(s.Serializer):
    """
    Parameter InnerDoc serializer
    """
    id = s.IntegerField()
    type = s.CharField()
    title_ru = s.CharField()
    title_ky = s.CharField()
    category = s.IntegerField()
    optional = s.BooleanField()


class V2OptionSerial(s.Serializer):
    """
    Option InnderDoc serializer
    """
    id = s.IntegerField()
    parameter = s.IntegerField()
    title_ru = s.CharField()
    title_ky = s.CharField()


class ProductV2ParameterSerializer(s.Serializer):
    """
    Product Parameter InnerDoc serializer
    """
    id = s.IntegerField()
    parameter = V2ParameterSerializer()
    option = V2OptionSerial()
    response = s.CharField()


class ProductV2UserSerializer(s.Serializer):
    """
    User serializer for Products document
    """
    id = s.IntegerField()
    name = s.CharField()
    email = s.CharField()
    phone = s.CharField()
    date_joined = s.CharField()
    last_active = s.CharField()
    photo = AbsolutePathImageField()
    language = s.CharField()
    business = s.IntegerField()
    is_business = s.BooleanField()


class ProductV2ContactsSerializer(s.Serializer):
    """
    Contacts serializer for elasticsearch object field
    """
    id = s.IntegerField()
    phone = s.CharField()


class ProductV2ListSerializer(s.Serializer):
    """
    Serialization of elasticsearch document for listing
    """
    id = s.IntegerField()
    user = ProductV2UserSerializer()
    category = s.IntegerField(source="category.id")
    state = s.CharField()
    title = s.CharField()
    upvote_date = s.DateTimeField()
    creation_date = s.DateTimeField()
    currency = s.CharField()
    initial_price = s.CharField()
    show_count = s.IntegerField()
    view_count = s.IntegerField()
    price_kgs = s.CharField()
    price_usd = s.CharField()

    def to_representation(self, instance):
        data = super().to_representation(instance)
        photos = []
        try:
            url = instance.photos[0].small_thumbnail
            if url:
                s3_url = config('AWS_S3_CUSTOM_DOMAIN', None)
                if s3_url:
                    media_host = f"https://{s3_url}"
                    photo = f"{media_host}/media/{url}"
                else:
                    photo = self.context['request'].build_absolute_uri(f"{settings.MEDIA_URL}{url}")
                photos.append({'photo': photo})

        except IndexError:
            pass

        data['photos'] = photos
        data['is_business'] = instance.user.is_business
        return data


class ProductV2LocationSerializer(s.Serializer):
    """
    Location serializer for Products document
    """
    id = s.IntegerField()
    title_ru = s.CharField()
    title_ky = s.CharField()
    type = s.CharField()
    request_ru = s.CharField()
    request_ky = s.CharField()
    parent = s.IntegerField()
    lat = s.CharField()
    lng = s.CharField()
    is_end = s.BooleanField()
    type_ru = s.CharField()
    type_ky = s.CharField()


class ProductV2PhotoSerializer(s.Serializer):
    id = s.IntegerField()
    photo = AbsolutePathImageField()
    small_thumbnail = AbsolutePathImageField()
    medium_thumbnail = AbsolutePathImageField()


class ProductV2DetailSerializer(s.Serializer):
    """
    Serializing detailed information about Product Documents
    """
    id = s.IntegerField()
    user = ProductV2UserSerializer()
    description = s.CharField()
    location = ProductV2LocationSerializer()
    state = s.CharField()
    upvote_date = s.DateTimeField()
    creation_date = s.DateTimeField()
    category = s.IntegerField(source="category.id")
    currency = s.CharField()
    initial_price = s.CharField()
    show_count = s.IntegerField()
    favorite_count = s.IntegerField()
    view_count = s.IntegerField()
    price_kgs = s.CharField()
    price_usd = s.CharField()
    rating = s.IntegerField()
    rating_disabled = s.BooleanField()
    like_count = s.IntegerField()
    photos = ProductV2PhotoSerializer(many=True)
    contacts = ProductV2ContactsSerializer(many=True)
    parameters = ProductV2ParameterSerializer(many=True)
