from datetime import datetime as dt
import datetime
from django.conf import settings
from django.db.models import Subquery, OuterRef, Count, F, Sum, Q
from rest_framework import serializers as s, exceptions

from category.models import Category
from category.serializers import ChildCategoryV2CleanSerializer
from payment.models import Tariff
from product.models import Product, ProductState, ProductPhoto, ProductReview
from product.serializers import ShortProductSerializer, ProductReviewSerializer
from users.serializers import PublicUserSerializer
from users.settings import RequestStatuses
from . import models
from .services import order_weekday, date_in


class BusinessContactSerializer(s.ModelSerializer):
    class Meta:
        model = models.BusinessContact
        fields = ('id', 'business', 'type', 'value')
        read_only_fields = ('business',)


class BusinessScheduleSerializer(s.ModelSerializer):
    class Meta:
        model = models.BusinessSchedule
        fields = ('id', 'business', 'weekday', 'time')
        read_only_fields = ('business',)


class BusinessBranchSerializer(s.ModelSerializer):
    lat = s.DecimalField(allow_null=False, max_digits=9, decimal_places=6)
    lng = s.DecimalField(allow_null=False, max_digits=9, decimal_places=6)

    class Meta:
        model = models.BusinessBranch
        fields = (
            'id',
            'business',
            'lat',
            'lng',
            'address',
        )
        read_only_fields = ('business',)


class BusinessBannerSerializer(s.ModelSerializer):
    class Meta:
        model = models.BusinessBanner
        fields = (
            'id',
            'business',
            'text',
            'photo',
        )
        read_only_fields = ('business',)


class ProductSerializerPhoto(s.ModelSerializer):
    class Meta:
        model = Product
        fields = ('id',)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        photo = ProductPhoto.objects.filter(product=instance).first()
        data["photo"] = None
        if photo:
            data["photo"] = self.context['request'].build_absolute_uri(f'{settings.MEDIA_URL}{photo.small_thumbnail}')
        return data


class BusinessCatalogSerializer(s.ModelSerializer):

    def __init__(self, *args, **kwargs):
        self.limit = kwargs.pop('limit', -1)
        super(BusinessCatalogSerializer, self).__init__(*args, **kwargs)

    products = s.SerializerMethodField()

    class Meta:
        model = models.BusinessCatalog
        fields = (
            'id',
            'name',
            'business',
            'product_count',
            'products',
        )

    def get_products(self, instance):
        qs = models.Product.objects.select_related('user').prefetch_related('favorites', 'likes'). \
            filter(catalog_product=instance.id)
        products_serializer = ProductSerializerPhoto
        if self.limit == -1:
            products_serializer = ShortProductSerializer
            photo_qs = ProductPhoto.objects.filter(product=OuterRef('pk')).values('small_thumbnail')
            qs = qs.annotate(photo=Subquery(photo_qs[:1]))
        else:
            qs = qs[:self.limit]

        return products_serializer(qs, many=True, context={'request': self.context['request']}).data

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["products_count"] = instance.products.count()
        return data

    def update(self, instance, validated_data):
        if validated_data.get("products"):
            products = Product.objects.filter(id__in=validated_data.get('products'))
            instance.products.add(*products)
        validated_data.pop('products')
        for key, val in validated_data.items():
            if hasattr(instance, key):
                setattr(instance, key, val)
        instance.save()
        return instance


class BusinessCatalogCreateSerializer(s.ModelSerializer):
    products = s.SerializerMethodField()

    class Meta:
        model = models.BusinessCatalog
        fields = ("id", "name", "business", 'products')
        read_only_fields = ("business",)

    def get_products(self, instance):
        return []

class BusinessCatalogPatchDestroySerializer(s.ModelSerializer):
    class Meta:
        model = models.BusinessCatalog
        fields = ('id', 'name', 'business', 'products')
        read_only_fields = ('business',)

class ReviewSerializer(s.ModelSerializer):
    class Meta:
        model = ProductReview
        fields = ('id', 'product', 'user', 'rating', 'review', 'creation_date')

class ShortBusinessSerializer(s.ModelSerializer):
    class Meta:
        model = models.Business
        fields = (
            'id', 'logo', 'user', 'name', 'description', 'creation_date',
            'banner', 'category', 'rating', 'product_count'
        )

    user = PublicUserSerializer()
    product_count = s.IntegerField(read_only=True)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['product_count'] = Product.objects.filter(user=instance.user, state=ProductState.ACTIVE).count()
        return data


class BusinessSerializer(s.ModelSerializer):
    """
    Detailed information about a request.user business
    """
    catalogs = s.SerializerMethodField()
    time_left = s.SerializerMethodField()

    class Meta:
        model = models.Business
        fields = (
            'id', 'user', 'name', 'description', 'creation_date', 'banner', 'category',
            'rating', 'product_limit', 'product_count', 'contacts', 'schedule',
            'branches', 'banners', 'catalogs', 'logo', 'delivery', 'time_left', 'is_not_demo'
        )
        read_only_fields = ('user', 'creation_date', 'rating', 'product_limit')

    contacts = BusinessContactSerializer(many=True)
    # schedule = BusinessScheduleSerializer(many=True)
    branches = BusinessBranchSerializer(many=True)
    banners = BusinessBannerSerializer(many=True)
    user = PublicUserSerializer(read_only=True)
    product_count = s.IntegerField(read_only=True)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['product_count'] = Product.objects.filter(user=instance.user, state=ProductState.ACTIVE).count()
        category = Category.objects.filter(id=instance.category.id).annotate(product_count=Count('products')).first()
        data['category'] = ChildCategoryV2CleanSerializer(category).data
        schedule = models.BusinessSchedule.objects.filter(business=instance)  ##
        data['schedule'] = BusinessScheduleSerializer(order_weekday(schedule), many=True).data  ##

        reviews = ProductReview.objects.filter(product__user=instance.user).annotate(reviews_count=Count('id'))
        u_c = reviews.filter(is_read=False).annotate(unread_reviews_count=Count('id'))

        data['reviews'] = ProductReviewSerializer(reviews, many=True, context={'request': self.context['request']}).data
        data['reviews_count'] = len(reviews.values_list('reviews_count'))
        data['unread_reviews_count'] = len(u_c.values_list('unread_reviews_count'))
        data['deactivate_date'] = instance.deactivate_date.date()
        return data

    def get_time_left(self, instance):
        formats = '%Y-%m-%d %H:%M:%S'
        end = instance.deactivate_date
        now = dt.now()
        time_left = None
        if end:
            end = dt.strptime(end.strftime(formats), formats)
            creation_date = instance.creation_date
            if end <= now:
                # one_month = Tariff.objects.filter(period=1).first().amount
                # if instance.user.balance >= one_month:
                #     instance.deactivate_date += datetime.timedelta(weeks=4) # adding a month
                #     instance.save()
                #     instance.user.balance -= one_month # we take it away for a month
                #     instance.user.save()
                # else:
                # #    instance.user.request_status = RequestStatuses.EXPIRED
                instance.is_active = False
                instance.save()
            else:
                time = end - dt.strptime(now.strftime(formats), formats)
                time_left = time.days if date_in(now, creation_date, end) else None
        return time_left

    def get_catalogs(self, instance):
        catalogs = models.BusinessCatalog.objects.filter(business=instance)
        return BusinessCatalogSerializer(catalogs, many=True, context={'request': self.context['request']}).data

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            if attr in ('name', 'description', 'banner', 'category', 'logo'):
                setattr(instance, attr, value)
        if 'contacts' in validated_data:
            contact_models = [models.BusinessContact(business=instance, **contact) for contact in
                              validated_data['contacts']]
            models.BusinessContact.objects.filter(business=instance).delete()
            models.BusinessContact.objects.bulk_create(contact_models)
        if 'schedule' in validated_data:
            schedule_models = [models.BusinessSchedule(business=instance, **schedule) for schedule in
                               validated_data['schedule']]
            models.BusinessSchedule.objects.filter(business=instance).delete()
            models.BusinessSchedule.objects.bulk_create(schedule_models)
        if 'branches' in validated_data:
            branch_models = [models.BusinessBranch(business=instance, **branch) for branch in
                             validated_data['branches']]
            models.BusinessBranch.objects.filter(business=instance).delete()
            models.BusinessBranch.objects.bulk_create(branch_models)
        if 'delivery' in validated_data:
            instance.delivery = validated_data['delivery']

        instance.save()
        return instance


class BusinessRequestSerializer(s.ModelSerializer):
    class Meta:
        model = models.Business
        fields = ('id', 'name', 'message', 'category')

    def create(self, validated_data):
        user = self.context['request'].user
        business = models.Business.objects.filter(user=user).first()
        if business:
            if business.is_active:
                raise exceptions.ValidationError('you have already business account', code='already_business')
            return business
        else:
            user.request_status = RequestStatuses.ON_REVIEW
            user.save()
            validated_data['description'] = validated_data['message']
            return super().create(validated_data)


class BusinessDeactivateSerializer(s.Serializer):
    message = s.CharField(required=True, allow_blank=False, allow_null=False)


class BusinessStatsSerializer(s.Serializer):
    show_count = s.IntegerField(required=True)
    view_count = s.IntegerField(required=True)
    call_count = s.IntegerField(required=True)
    message_count = s.IntegerField(required=True)
    # favorite_count = s.IntegerField(required=True)
    # review_count = s.IntegerField(required=True)
    # like_count = s.IntegerField(required=True)
    # coverage = s.IntegerField(required=True)
    #
    # def to_representation(self, instance):
    #     return instance
