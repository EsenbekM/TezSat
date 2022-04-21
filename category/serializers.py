from rest_framework import serializers as s

from business.models import Business
from product.models import Product, ProductState
from tezsat.utils import get_children_id, get_children_id_wo_parent
from . import models
from .models import Category
from .settings import PRODUCT_MULTIPLE


class OptionSerializer(s.ModelSerializer):
    class Meta:
        model = models.Option
        fields = ('id', 'title_ru', 'title_ky', 'parameter')


class SelectedParameterSerializer(s.ModelSerializer):
    class Meta:
        model = models.Parameter
        fields = ('id', 'title_ru', 'title_ky', 'category', 'optional', 'type')


class ParameterSerializer(s.ModelSerializer):
    class Meta:
        model = models.Parameter
        fields = ('id', 'title_ru', 'title_ky', 'category', 'type', 'optional', 'options', 'is_many')

    options = OptionSerializer(many=True)


class ChildCategorySerializer(s.ModelSerializer):
    class Meta:
        model = models.Category
        fields = (
            'id', 'title_ru', 'title_ky', 'title_slug', 'icon', 'large_icon', 'parent', 'is_end', 'product_count',
            'business_count'
        )

    is_end = s.BooleanField(read_only=True)
    product_count = s.IntegerField(read_only=True)
    business_count = s.IntegerField(read_only=True)

    def to_representation(self, instance):
        # todo: determine how to optimize
        data = super().to_representation(instance)
        if hasattr(instance, 'children_count'):
            data['is_end'] = 0 == instance.children_count
        else:
            data['is_end'] = 0 == instance.children.count()
        ids = get_children_id(models.Category, [instance.id])
        data['product_count'] = PRODUCT_MULTIPLE * Product.objects.filter(state=ProductState.ACTIVE,
                                                                          category_id__in=ids).count()
        data['business_count'] = Business.objects.filter(category_id__in=ids, is_active=True).count()
        return data


class ChildCategoryV2Serializer(s.ModelSerializer):
    class Meta:
        model = models.Category
        fields = ('id', 'title_ru', 'title_ky', 'icon', "title_slug", "product_count", 'parent', 'is_end')

    is_end = s.BooleanField(read_only=True)

    def to_representation(self, instance):
        # todo: determine how to optimize
        data = super().to_representation(instance)
        if hasattr(instance, 'children_count'):
            data['is_end'] = 0 == instance.children_count
        else:
            data['is_end'] = 0 == instance.children.count()
        return data


class ChildCategoryV2CleanSerializer(s.ModelSerializer):
    class Meta:
        model = models.Category
        fields = ('id', 'title_ru', 'title_ky', 'title_slug', 'icon', 'parent', 'order',)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['product_count'] = instance.product_count
        return data

class CategorySerializer(s.ModelSerializer):
    class Meta:
        model = models.Category
        fields = ('id', 'title_ru', 'title_ky', 'title_slug', 'icon', 'parent', 'children')

    children = ChildCategorySerializer(many=True)


class CategoryV2Serializer(s.ModelSerializer):
    class Meta:
        model = models.Category
        fields = ('id', 'title_ru', 'title_ky', 'icon', "title_slug", 'parent', 'children', 'order')

    children = ChildCategoryV2Serializer(many=True)
    def to_representation(self, instance):
        data = super(CategoryV2Serializer, self).to_representation(instance)
        data['product_count'] = instance.product_count
        return data

class CategoryV2GetParentsSerializer(s.ModelSerializer):
    class Meta:
        model = models.Category
        fields = ('id', 'title_ru', 'title_ky', 'icon', 'title_slug')