from django_filters import rest_framework
from django_filters.constants import EMPTY_VALUES

from category.models import Category
from location.models import Location
from product.models import Product
from tezsat.utils import get_children_id


class RecursiveFilter(rest_framework.Filter):

    def __init__(self, field_name=None, lookup_expr=None, *, label=None,
                 method=None, distinct=False, recursive_model=None, exclude=False, **kwargs):
        if not recursive_model:
            raise Exception("Recursive model attribute required for filtering!")
        self.recursive_model = recursive_model
        super(RecursiveFilter, self).__init__(field_name=None, lookup_expr=None, label=None,
                 method=None, distinct=False, exclude=False, **kwargs)

    def filter(self, qs, value: str):
        if value in EMPTY_VALUES:
            return qs
        try:
            raw_ids = [int(i) for i in value.split(",")]
        except ValueError:
            return qs
        ids = get_children_id(self.recursive_model, raw_ids)
        field = {
            f'{self.field_name}_id__in': ids
        }
        return qs.filter(**field)


class ProductFilterSet(rest_framework.FilterSet):
    category = RecursiveFilter(lookup_expr='category', recursive_model=Category)
    location = RecursiveFilter(lookup_expr='location', recursive_model=Location)

    class Meta:
        model = Product
        fields = [
            'category',
            'location',
        ]
