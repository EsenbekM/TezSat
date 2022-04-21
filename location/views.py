from rest_framework import viewsets, decorators, response
from .serializers import LocationSerializer, ChildLocationSerializer
from .models import Location
from tezsat.mixins import ActionSerializerClassMixin
from django.db.models import Count
from drf_yasg2.utils import swagger_auto_schema


class LocationView(viewsets.ReadOnlyModelViewSet):
    pagination_class = None
    serializer_class = LocationSerializer
    authentication_classes = ()
    permission_classes = ()

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset.first())
        return response.Response(serializer.data)

    def filter_queryset(self, queryset):
        if self.action == 'list':
            return queryset.filter(parent__isnull=True)
        return queryset

    def get_queryset(self):
        return Location.objects\
            .annotate(children_count=Count('children'), product_count=Count('products'))\
            .order_by('order')

    def _get_serialized_children(self, dict_children, result):
        for parent, children in dict_children.items():
            parent_data = ChildLocationSerializer(instance=parent).data
            parent_children = []
            if children is not None:
                self._get_serialized_children(children, parent_children)
            parent_data['children'] = parent_children
            result.append(parent_data)

    @decorators.action(['GET'], detail=False)
    @swagger_auto_schema(responses={'200': ChildLocationSerializer()}, tags=['location'])
    def full(self, request):
        parent_location = Location.objects.filter(parent__isnull=True).order_by('order').first()
        data = ChildLocationSerializer(instance=parent_location).data
        dict_children = parent_location.get_all_children()
        children = []
        self._get_serialized_children(dict_children, children)
        data['children'] = children
        return response.Response(data=data)

    @decorators.action(['GET'], detail=False)
    @swagger_auto_schema(responses={'200': ChildLocationSerializer(many=True)}, tags=['location'])
    def non_structured(self, request):
        qs = self.get_queryset().exclude(title_ru='/', title_ky='/')
        serializers = ChildLocationSerializer(instance=qs, many=True)
        return response.Response(data=serializers.data)
