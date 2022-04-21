from django_filters.constants import EMPTY_VALUES
from rest_framework.exceptions import ValidationError
from rest_framework.filters import SearchFilter, BaseFilterBackend

from product.settings import CurrencyType


class ProductV2Filter(BaseFilterBackend):
    """
    Filter Backend for elasticsearch filtering
    """
    materialized_paths = ['category', 'location']

    def filter_by_user(self, request, queryset):
        user_id = request.query_params.get('user', '')
        if user_id in EMPTY_VALUES:
            return queryset

        try:
            user_id = int(user_id)
        except ValueError:
            raise ValidationError({'error': 'All parameters must be valid integers'})

        queryset = queryset.filter('term', **{'user.id': user_id})

        return queryset

    def filter_parameters(self, request, queryset):
        options = request.query_params.get('options', '')
        if options in EMPTY_VALUES:
            return queryset

        try:
            options_list = list(map(int, options.split(",")))
        except ValueError:
            raise ValidationError({'error': 'All parameters must be valid integers'})

        queryset = queryset.filter('terms', **{'parameters__option__id': options_list})
        return queryset

    def filter_price(self, request, queryset):
        currency = request.query_params.get('currency')
        if not currency or currency not in CurrencyType.all():
            return queryset
        fields = {}
        for option in ('gte', 'lte'):
            param = f'price__{option}'
            if param in request.query_params:
                fields[option] = request.query_params[param]
        if fields:
            return queryset.filter('range', **{f"price_{currency.lower()}": fields})
        return queryset

    def filter_business(self, request, queryset):
        is_business = request.GET.get('is_business', None)
        if is_business is None:
            return queryset
        is_business = is_business.lower()
        if is_business == 'true':
            return queryset.filter('bool', user__is_business=True)
        return queryset

    def filter_path(self, request, queryset):
        for field in self.materialized_paths:
            param = request.query_params.get(field, '')
            if param not in EMPTY_VALUES:
                value_list = param.split(",")
                filter_field = {f'{field}_path': value_list}
                queryset = queryset.filter('terms', **filter_field)

        return queryset

    def filter_queryset(self, request, queryset, view):
        queryset = self.filter_by_user(request, queryset)
        queryset = self.filter_business(request, queryset)
        queryset = self.filter_price(request, queryset)
        queryset = self.filter_path(request, queryset)
        queryset = self.filter_parameters(request, queryset)
        return queryset


class FullTextSearchFilter(SearchFilter):
    """
    Filter by full text search with elasticsearch
    """

    def filter_queryset(self, request, queryset, view):
        search_fields = self.get_search_fields(view, request)
        search_terms = self.get_search_terms(request)

        if not search_fields or not search_terms:
            return queryset
        queryset = queryset.query('multi_match', query=" ".join(search_terms), fields=search_fields)

        return queryset
