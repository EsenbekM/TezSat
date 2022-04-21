from rest_framework import viewsets, decorators, mixins
from rest_framework.response import Response
from . import serializers as s, models
from tezsat.mixins import ActionSerializerClassMixin
from rest_framework.decorators import action
from django.db.models import Count
from drf_yasg2.utils import swagger_auto_schema
from tezsat.utils import get_children_id
from product.models import Product
from djqscsv import render_to_csv_response
from .models import Category


class CategoryView(ActionSerializerClassMixin, viewsets.ReadOnlyModelViewSet):
    pagination_class = None
    serializer_class = s.CategorySerializer
    authentication_classes = ()
    permission_classes = ()

    action_serializer_class = {
        "list": s.ChildCategorySerializer
    }

    def filter_queryset(self, queryset):
        if self.action == 'list':
            return queryset.filter(parent__isnull=True).all()
        return queryset

    def get_queryset(self):
        return models.Category.objects \
            .prefetch_related('children') \
            .annotate(children_count=Count('children')) \
            .order_by('order') \
            .all()

    @action(detail=True)
    @swagger_auto_schema(responses={'200': s.ParameterSerializer(many=True)}, tags=['category'])
    def parameters(self, request, pk):
        category = self.get_object()
        params = category.get_parameters()
        response = []
        for param in params:
            response.append(
                s.ParameterSerializer(instance=param).data
            )
        return Response(response)

    @action(['GET'], detail=True, permission_classes=())
    def top_products(self, request, pk):
        ids = get_children_id(Category, [pk])
        product = Product.objects.filter(category__in=ids).order_by('-view_count'). \
            values('view_count', 'category__title_ky', 'category__title_ru', 'title', 'state', 'location__title_ru')
        return render_to_csv_response(product)


class CategoryV2View(viewsets.ReadOnlyModelViewSet):
    pagination_class = None
    serializer_class = s.CategoryV2Serializer
    authentication_classes = ()
    permission_classes = ()

    def get_queryset(self):
        return models.Category.objects \
            .prefetch_related('children', 'children__children') \
            .filter(parent__isnull=True) \
            .order_by('order') \
            .annotate(product_count=Count('products')) \
            .all()

    @decorators.action(['GET'], detail=False)
    @swagger_auto_schema(responses={'200': s.ChildCategoryV2CleanSerializer(many=True)}, tags=['category'])
    def non_structured(self, request):
        qs = Category.objects.all().annotate(product_count=Count('products'))
        return Response(data=s.ChildCategoryV2CleanSerializer(instance=qs, many=True).data)
