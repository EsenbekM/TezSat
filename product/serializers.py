from django.conf import settings
from django.core.files.storage import default_storage
from django.db.models import Subquery, OuterRef, F
from rest_framework import serializers as s, exceptions

from category.serializers import SelectedParameterSerializer, OptionSerializer
from category.settings import ParameterType
from location.models import Location
from location.serializers import ChildLocationSerializer
from location.settings import LocationType
from notification.job import stared
from tezsat.utils import get_filename
from users.serializers import PublicUserSerializer
from . import models
from .models import Rate
from .settings import PHOTO_TMP_DIR, PHOTO_UPLOAD_DIR, ProductState, CurrencyType


class CurrencySerializer(s.ModelSerializer):
    class Meta:
        model = models.Rate
        fields = ('id', 'currency', 'rate')


class ProductContactSerializer(s.ModelSerializer):
    class Meta:
        model = models.ProductContact
        fields = ('id', 'phone')


class ProductPhotoSerializer(s.ModelSerializer):
    class Meta:
        model = models.ProductPhoto
        fields = ('id', 'photo', 'medium_thumbnail', 'small_thumbnail', 'filename')
        read_only_fields = ('photo', 'medium_thumbnail', 'small_thumbnail')

    filename = s.CharField(required=True, write_only=True)

    def validate_filename(self, filename):
        if not default_storage.exists(f'{PHOTO_TMP_DIR}/{filename}') \
                and not default_storage.exists(f'{PHOTO_UPLOAD_DIR}/{filename}'):
            raise exceptions.ValidationError('file not found')
        return filename

    def create(self, validated_data):
        product_photo = models.ProductPhoto(product=validated_data['product'], photo=None)
        with default_storage.open(f'{PHOTO_TMP_DIR}/{validated_data["filename"]}') as file:
            product_photo.photo.save(validated_data['filename'], file)
            product_photo.save()
            default_storage.delete(f'{PHOTO_TMP_DIR}/{validated_data["filename"]}')
            return product_photo


class ProductParameterSerializer(s.ModelSerializer):
    class Meta:
        model = models.ProductParameter
        fields = ('id', 'parameter', 'option', 'response')
        write_only_fields = ('parameter', 'option')

    def to_representation(self, instance):
        data = super().to_representation(instance)
        parameter = SelectedParameterSerializer(instance=instance.parameter)
        data['option'] = None
        if instance.parameter.type == ParameterType.SELECT:
            option = OptionSerializer(instance=instance.option)
            data['option'] = option.data
        data['parameter'] = parameter.data
        return data


class ProductParameterResponseSerializer(s.ModelSerializer):
    class Meta:
        model = models.ProductParameter
        fields = ('id', 'parameter', 'option', 'response')
        read_only_fields = fields

    option = OptionSerializer(read_only=True)
    parameter = SelectedParameterSerializer(read_only=True)


class PhotoResponseSerializer(s.Serializer):
    photo = s.URLField(read_only=True)


class CustomRepresentation:
    def to_representation(self, instance):
        data = super().to_representation(instance)
        if hasattr(instance, 'favorite_count'):
            data['favorite_count'] = instance.favorite_count
        else:
            data['favorite_count'] = instance.favorites.count()
        data['photos'] = []
        if instance.photo:
            photos = {
                "photo": self.context['request'].build_absolute_uri(f'{settings.MEDIA_URL}{instance.photo}')
            }
            data['photos'].append(photos)
        return data


class NakedProductSerializer(CustomRepresentation, s.ModelSerializer):
    class Meta:
        model = models.Product
        fields = ('id', 'user', 'title', 'price_kgs', 'price_usd', 'show_count', 'view_count', 'state')


class ShortProductSerializer(CustomRepresentation, s.ModelSerializer):
    class Meta:
        model = models.Product
        fields = ('id', 'user', 'title', 'location', 'currency', 'initial_price', 'price_kgs', 'price_usd', 'show_count',
                  'view_count', 'state', 'rating', 'rating_disabled', 'category', 'discount_price_kgs',
                  'discount_price_usd', 'discount', 'creation_date')

    user = PublicUserSerializer()
    location = ChildLocationSerializer()
    # photos = ProductPhotoSerializer(many=True)



class ProductSerializer(s.ModelSerializer):
    class Meta:
        model = models.Product
        fields = ('id', 'user', 'description',
                  'location', 'currency', 'initial_price', 'price_kgs', 'price_usd', 'category',
                  'state', 'creation_date', 'upvote_date', 'show_count', 'view_count',
                  'contacts', 'photos', 'parameters', 'price', 'rating', 'rating_disabled', 'discount_price_kgs',
                  'discount_price_usd', 'discount')
        read_only_fields = (
            'creation_date', 'price_kgs', 'price_usd', 'show_count', 'view_count', 'upvote_date', 'initial_price',
            'rating'
        )

    user = PublicUserSerializer(read_only=True)
    contacts = ProductContactSerializer(many=True, required=True)
    photos = ProductPhotoSerializer(many=True, required=True)
    parameters = ProductParameterSerializer(many=True)
    price = s.DecimalField(max_digits=20, decimal_places=2, required=True, write_only=True)
    state = s.ChoiceField((ProductState.ACTIVE, ProductState.INACTIVE), required=False)

    def validate_state(self, state):
        if self.instance.state in (ProductState.ON_REVIEW, ProductState.BLOCKED, ProductState.DELETED):
            raise exceptions.ValidationError('You cannot change state of product')
        return state

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['favorite_count'] = instance.favorites.count()
        data['like_count'] = instance.likes.count()
        data['location'] = ChildLocationSerializer(instance=instance.location).data
        return data

    def validate_parameters(self, params):
        parameters = {}
        errors = []
        is_error = False
        for param in params:
            if 'parameter' not in param:
                errors.append({
                    "parameter": "field required",
                })
                is_error = True
                continue
            parameters[param['parameter'].id] = param
            if param['parameter'].type == ParameterType.SELECT:
                if 'option' not in param:
                    errors.append({
                        "option": "field required",
                    })
                    is_error = True
                else:
                    errors.append({})
                    if not param['parameter'].options.filter(id=param['option'].id).exists():
                        is_error = True
                        errors.append({
                            "option": "invalid option for given parameter"
                        })
                    else:
                        errors.append({})
            else:
                if 'response' not in param:
                    errors.append({
                        "response": "field required",
                    })
                    is_error = True
                else:
                    errors.append({})
        if is_error:
            raise exceptions.ValidationError(errors)
        return params

    def validate(self, attrs):
        if 'category' in attrs:
            category = attrs['category']
            errors = []
            for param in category.get_parameters():
                if not param.optional and param.id not in attrs['parameters']:
                    errors.append({
                        'parameter': f'parameter with id {param.id} required'
                    })
            if errors:
                raise exceptions.ValidationError({"parameters": errors}, 'required')

        # business product limit validation
        if hasattr(self.context['request'].user, 'business') and self.context['request'].user.business.is_active:
            attrs['is_business'] = True
            if self.context['request'].method == 'POST':
                business = self.context['request'].user.business
                product_count = self.context['request'].user.products.count()

                if business.product_limit is not None and product_count >= business.product_limit:
                    raise exceptions.ValidationError({'non_field_error': 'product count limit reached'},
                                                     code='product_limit')
        else:
            attrs['is_business'] = False
        return attrs

    def create(self, validated_data):
        if validated_data['is_business']:
            rating_disabled = validated_data.get('rating_disabled', False)
        else:
            rating_disabled = True
        product = models.Product(user=self.context['request'].user,
                                 description=validated_data['description'],
                                 location=validated_data['location'],
                                 category=validated_data['category'],
                                 currency=validated_data['currency'],
                                 price=validated_data['price'],
                                 rating_disabled=rating_disabled)
        if 'discount' in validated_data:
            discount = validated_data['discount']
            usd = Rate.objects.filter(currency=CurrencyType.USD).first()
            if discount == 0:
                product.discount_price_usd = None
                product.discount_price_kgs = None
            else:
                if product.currency == CurrencyType.USD:
                    product.discount_price_usd = discount
                    product.discount_price_kgs = discount * usd.rate
                    product.discount = (product.initial_price - product.discount_price_usd) * 100 // product.initial_price
                else:
                    product.discount_price_kgs = discount
                    product.discount_price_usd = discount / usd.rate
                    product.discount = (product.initial_price - product.discount_price_kgs) * 100 // product.initial_price
                    
        product.save()
        contact_models = [models.ProductContact(product=product, **contact) for contact in validated_data['contacts']]
        parameter_models = [models.ProductParameter(product=product, **fields) for fields in
                            validated_data['parameters'][:]]
        models.ProductContact.objects.bulk_create(contact_models)
        models.ProductParameter.objects.bulk_create(parameter_models)

        photo_serializers = [ProductPhotoSerializer(data=photo, context={'request': self.context['request']})
                             for photo in validated_data['photos']]
        for photo_serializer in photo_serializers:
            photo_serializer.is_valid(True)
            photo_serializer.save(product=product)
        return product

    def update(self, instance, validated_data):
        change_state = False
        for attr, value in validated_data.items():
            if attr in ('description', 'location', 'category', 'currency', 'price', 'rating_disabled'):
                if not validated_data['is_business'] and attr == 'rating_disabled':
                    continue
                setattr(instance, attr, value)
                change_state = True
        if 'contacts' in validated_data:
            change_state = True
            contact_models = [models.ProductContact(product=instance, **contact) for contact in
                              validated_data['contacts']]
            models.ProductContact.objects.filter(product=instance).delete()
            models.ProductContact.objects.bulk_create(contact_models)
        # TODO discount
        if 'discount' in validated_data:
            usd = Rate.objects.filter(currency=CurrencyType.USD).first()
            discount = validated_data['discount']
            if discount == 0:
                instance.discount_price_usd = None
                instance.discount_price_kgs = None
            else:
                if instance.currency == CurrencyType.USD:
                    instance.discount_price_usd = discount
                    instance.discount_price_kgs = discount * usd.rate
                    instance.discount = (instance.initial_price - instance.discount_price_usd) * 100 // instance.initial_price
                else:
                    instance.discount_price_kgs = discount
                    instance.discount_price_usd = discount / usd.rate
                    instance.discount = (instance.initial_price - instance.discount_price_kgs) * 100 // instance.initial_price
                    
        if 'parameters' in validated_data:
            change_state = True
            parameter_models = [models.ProductParameter(product=instance, **fields) for fields in
                            validated_data['parameters'][:]]
            models.ProductParameter.objects.filter(product=instance).delete()
            models.ProductParameter.objects.bulk_create(parameter_models)
        if 'photos' in validated_data:
            change_state = True
            exist_photos = set([item.photo.name.rsplit('/', 1)[1] for item in instance.photos.all()])
            photos = set([item['filename'] for item in validated_data['photos']])
            to_delete = exist_photos.difference(photos)
            to_create = photos.difference(exist_photos)
            models.ProductPhoto.objects.filter(
                photo__in=[f'{PHOTO_UPLOAD_DIR}/{filename}' for filename in to_delete]).delete()
            photo_serializers = [
                ProductPhotoSerializer(data={'filename': filename}, context={'request': self.context['request']})
                for filename in to_create]
            for photo_serializer in photo_serializers:
                photo_serializer.is_valid(True)
                photo_serializer.save(product=instance)
        if hasattr(self.context['request'].user, 'business') and self.context['request'].user.business.is_active:
            change_state = False
        if change_state:
            instance.state = ProductState.ON_REVIEW
        else:
            if 'state' in validated_data:
                instance.state = validated_data['state']
        instance.save()
        return instance


class PhotoUploadSerializer(s.Serializer):
    photo = s.ImageField(required=True)

    def create(self, validated_data):
        # photo = compress_image(validated_data['photo'])
        name = get_filename(validated_data['photo'].name)
        default_storage.save(f'{PHOTO_TMP_DIR}/{name}', validated_data['photo'])

        return {'filename': name}

    def to_representation(self, instance):
        return instance


class FavoriteCreationSerializer(s.Serializer):
    product = s.IntegerField(required=True)

    def validate_product(self, product_id):
        product = models.Product.objects.filter(id=product_id, state=ProductState.ACTIVE).first()
        if not product:
            raise exceptions.ValidationError('product not found')
        return product

    def create(self, validated_data):
        user = self.context['request'].user
        user.favorites.add(validated_data['product'])
        stared(user, validated_data['product'])
        return {}

    def to_representation(self, instance):
        return {}


class LikeCreationSerializer(s.Serializer):
    product = s.IntegerField(required=True)

    def validate_product(self, product_id):
        product = models.Product.objects.filter(id=product_id, state=ProductState.ACTIVE).first()
        if not product:
            raise exceptions.ValidationError('product not found')
        return product

    def create(self, validated_data):
        user = self.context['request'].user
        user.likes.add(validated_data['product'])
        return {}

    def to_representation(self, instance):
        return {}


class ProductReviewSerializer(s.ModelSerializer):
    product = s.SerializerMethodField()

    class Meta:
        model = models.ProductReview
        fields = ('id', 'product', 'user', 'rating', 'review', 'creation_date', 'response', 'response_date', 'is_read')
        read_only_fields = ('product', 'user', 'creation_date', 'response', 'response_date')

    user = PublicUserSerializer(read_only=True)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['is_claimed'] = bool(instance.claim)
        return data

    def get_product(self, instance):
        qs = models.Product.objects.select_related('user').prefetch_related('favorites', 'likes'). \
            filter(reviews=instance.id)
        products_serializer = ShortProductSerializer
        photo_qs = models.ProductPhoto.objects.filter(product=OuterRef('pk')).values('small_thumbnail')
        qs = qs.annotate(photo=Subquery(photo_qs[:1]))
        return products_serializer(qs, many=True, context={'request': self.context['request']}, partial=True).data

class ClaimSerializer(s.ModelSerializer):
    class Meta:
        model = models.Claim
        fields = ('id', 'product', 'user', 'type', 'message')

class ClaimCategorySerializer(s.ModelSerializer):
    class Meta:
        model = models.ClaimCategory
        fields = ('id', 'icon', 'claim_type', 'language')

class ProductReviewResponseSerializer(s.Serializer):
    response = s.CharField(required=True)


class ProductReviewClaimSerializer(s.Serializer):
    message = s.CharField(required=True)


class ProductStatisticSerializer(s.ModelSerializer):
    class Meta:
        model = models.Product
        fields = ('id', 'show_count', 'view_count', 'call_count', 'message_count', 'rating', 'rating_disabled',
                  'favorite_count', 'review_count', 'like_count')

    favorite_count = s.IntegerField()
    review_count = s.IntegerField()
    like_count = s.IntegerField()

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['coverage'] = data['show_count']
        return data


class ShortProductWithStatsSerializer(CustomRepresentation, s.ModelSerializer):
    class Meta:
        model = models.Product
        fields = ('id', 'user', 'title', 'currency', 'initial_price', 'price_kgs', 'price_usd', 'state',
                  'rating', 'rating_disabled', 'call_count', 'message_count', 'rating', 'show_count',
                  'view_count', 'favorite_count', 'review_count', 'like_count')

    favorite_count = s.IntegerField()
    review_count = s.IntegerField()
    like_count = s.IntegerField()

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['coverage'] = data['show_count']
        return data
