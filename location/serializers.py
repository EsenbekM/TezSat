from rest_framework import serializers as s
from .models import Location
from .settings import LocationType


class ChildLocationSerializer(s.ModelSerializer):
    class Meta:
        model = Location
        fields = ('id', 'title_ru', 'title_ky', 'type', 'request_ru', 'request_ky', 'parent', 'lat', 'lng', 'is_end',
                  'type_ky', 'type_ru', 'region')

    is_end = s.BooleanField(read_only=True)
    type_ru = s.CharField(read_only=True)
    type_ky = s.CharField(read_only=True)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if hasattr(instance, 'children_count'):
            data['is_end'] = 0 == instance.children_count
        else:
            data['is_end'] = 0 == instance.children.count()
        data['type_ru'] = LocationType.get_notation(instance.type, LocationType.ru)
        data['type_ky'] = LocationType.get_notation(instance.type, LocationType.ky)
        return data


class LocationSerializer(s.ModelSerializer):
    class Meta:
        model = Location
        fields = ('id', 'title_ru', 'title_ky', 'type', 'request_ru', 'request_ky', 'children', 'lat', 'lng', 'is_end',
                  'type_ky', 'type_ru', 'region')

    is_end = s.BooleanField(read_only=True)
    type_ru = s.CharField(read_only=True)
    type_ky = s.CharField(read_only=True)
    children = ChildLocationSerializer(many=True)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if hasattr(instance, 'children_count'):
            data['is_end'] = 0 == instance.children_count
        else:
            data['is_end'] = 0 == instance.children.count()
        data['type_ru'] = LocationType.get_notation(instance.type, LocationType.ru)
        data['type_ky'] = LocationType.get_notation(instance.type, LocationType.ky)
        return data
