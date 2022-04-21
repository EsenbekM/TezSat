from django.db.models import Q
from firebase_admin import auth
from rest_framework import serializers as s, exceptions

from category.models import Category
from category.serializers import ChildCategoryV2CleanSerializer
from .exceptions import UserAlreadyExist
from .models import User
from .services import expired_limit_
from .settings import Lang
from .utils import get_param_from_firebase


class PublicUserSerializer(s.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'name', 'email', 'phone', 'date_joined', 'last_active', 'photo', 'language', 'is_business',
                  'business', 'balance')
        read_only_fields = ('business',)

    is_business = s.BooleanField(read_only=True)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if hasattr(instance, 'business'):
            data['is_business'] = instance.business.is_active
            data['business'] = instance.business.id if instance.business.is_active else None
            data['business_name']=instance.business.name if instance.business.is_active else None
        else:
            data['is_business'] = False
            data['business'] = None
            data['business_name'] = None
        return data


class UserSerializer(s.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id', 'name', 'email', 'phone', 'date_joined', 'last_active', 'photo', 'firebase_uid', 'fcm_id', 'location',
            'language', 'platform', 'sign_in_method', 'is_business', 'provider', 'business', 'has_password',
            'request_status', 'balance')
        read_only_fields = ('date_joined', 'firebase_uid', 'business')

    email = s.CharField(required=False, allow_null=True, allow_blank=True)
    phone = s.CharField(required=False, allow_null=True, allow_blank=True)
    is_business = s.BooleanField(read_only=True)
    has_password = s.BooleanField(read_only=True)

    def validate_email(self, value):
        if value is None or (isinstance(value, str) and len(value) == 0):
            return None
        try:
            decoded = auth.verify_id_token(value)
        except auth.ExpiredIdTokenError:
            raise exceptions.ValidationError({"email": 'token expired'})
        except Exception:
            raise exceptions.ValidationError({"email": 'invalid token'})

        data, provider = get_param_from_firebase(decoded)
        if provider != 'password':
            raise exceptions.ValidationError({"email": "invalid provider"})
        user = User.objects.filter(email__iexact=data['email']).first()
        if not user:
            return data['email']
        if user.id != self.context['request'].user.id:
            raise UserAlreadyExist()
        return data['email']

    def validate_phone(self, value):
        if value is None or (isinstance(value, str) and len(value) == 0):
            return None
        try:
            decoded = auth.verify_id_token(value)
        except auth.ExpiredIdTokenError:
            raise exceptions.ValidationError({"phone": 'token expired'})
        except Exception:
            raise exceptions.ValidationError({"phone": 'invalid token'})

        data, provider = get_param_from_firebase(decoded)
        if provider != 'phone':
            raise exceptions.ValidationError({"phone": "invalid provider"})
        user = User.objects.filter(phone=data['phone']).first()
        if not user:
            return data['phone']
        if user.id != self.context['request'].user.id:
            raise UserAlreadyExist()
        return data['phone']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if hasattr(instance, 'business'):
            data['is_business'] = instance.business.is_active
            data['business'] = instance.business.id if instance.business.is_active else None
            data['business_name'] = instance.business.name if instance.business.is_active else None
        else:
            data['is_business'] = False
            data['business'] = None
            data['business_name'] = None
        data['request_status'] = expired_limit_(instance)
        data['has_password'] = bool(instance.password)
        return data


class LoginResponseSerializer(s.Serializer):
    user = UserSerializer()
    refresh = s.CharField()
    access = s.CharField()


class PasswordField(s.CharField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('style', {})

        kwargs['style']['input_type'] = 'password'
        kwargs['write_only'] = True

        super().__init__(*args, **kwargs)


class LoginSerializer(s.Serializer):
    login = s.CharField(required=True, allow_blank=False, allow_null=False)
    password = PasswordField(required=True, allow_blank=False, allow_null=False)
    language = s.ChoiceField(choices=(Lang.KY, Lang.RU), default=Lang.KY)


class BaseFirebaseSerializer(s.Serializer):
    token = s.CharField(required=True)

    def validate(self, attrs):
        attrs = super().validate(attrs)
        token = attrs['token']
        try:
            decoded = auth.verify_id_token(token)
        except auth.ExpiredIdTokenError:
            raise exceptions.ValidationError({"token": 'token expired'})
        except Exception:
            raise exceptions.ValidationError({"token": 'invalid token'})
        return {
            **attrs,
            "decoded": decoded,
        }


class SocialLoginSerializer(BaseFirebaseSerializer):
    language = s.ChoiceField(choices=(Lang.KY, Lang.RU), default=Lang.KY)
    phone = s.CharField(required=False)


class FirebaseSignUpSerializer(BaseFirebaseSerializer):
    password = PasswordField(required=False)
    name = s.CharField(required=True)
    language = s.ChoiceField(choices=(Lang.KY, Lang.RU), default=Lang.KY)


class PasswordRecoverySerializer(BaseFirebaseSerializer):
    password = PasswordField(required=True)


class UpdatePasswordSerializer(s.Serializer):
    old_password = PasswordField(required=True)
    new_password = PasswordField(required=True)

    def validate_old_password(self, value):
        if self.instance.password is None:
            raise exceptions.ValidationError('your account do not have a password set up')
        if not self.instance.check_password(value):
            raise exceptions.ValidationError('incorrect password')
        return value

    def update(self, instance, validated_data):
        instance.set_password(validated_data['new_password'])
        instance.save()
        return instance


class ExistenceSerializer(s.Serializer):
    login = s.CharField(required=True)

    def validate_login(self, value):
        try:
            User.objects.get(Q(email__iexact=value) | Q(phone=value))
        except User.DoesNotExist:
            return value
        else:
            raise UserAlreadyExist()


class FavoriteCategoryCreationSerializer(s.Serializer):
    categories = s.ListField(child=s.IntegerField(required=True), required=True)

    def validate_categories(self, values):
        values_set = set(values)
        categories = Category.objects.filter(id__in=values_set).all()
        categories_set = set([c.id for c in categories])
        diff = values_set.difference(categories_set)
        if diff:
            raise s.ValidationError(list(diff), code='not_found')
        return categories

    def create(self, validated_data):
        user = self.context['request'].user
        user.categories.set(validated_data['categories'])
        return validated_data['categories']

    def to_representation(self, instance):
        return {"categories": ChildCategoryV2CleanSerializer(instance=instance, many=True).data}
