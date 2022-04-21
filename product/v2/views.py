from django_q.tasks import async_task
from rest_framework import mixins, viewsets, generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from category.documents import ProductKeyword
from product.documents import ProductDocument
from product.jobs import update_both_view_count
from product.utils import get_elastic_object_or_404
from product.v2 import serializers
from product.v2.filters import FullTextSearchFilter, ProductV2Filter
from product.v2.paginators import ElasticLimitPagination
from users.services import get_translit_word


class SuggestionsView(generics.GenericAPIView):
    """
    Suggestion view for the search as you type functionality, search param ?query=
    """
    serializer_class = serializers.SuggestionsSerializer
    permission_classes = (AllowAny,)

    def get_queryset(self):
        query = self.request.query_params.get('query', '')
        # HERE
        word = get_translit_word(query)
        s = ProductKeyword.search()
        s = s.source(includes=["id", "icon", "is_category", "title"])
        s = s.suggest(
            prefix=query,
            text=query,
            name='recommendations',
            completion={
                'field': 'title_suggest',
                'size': 10,
                'skip_duplicates': True,
                'fuzzy': {
                    'fuzziness': 1,
                    "min_length": 5,
                },
            }
        )
        result = s.execute()
        options = result.suggest['recommendations'][0]['options']
        sources = [i['_source'] for i in options]
        return sources

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ProductViewV2(mixins.ListModelMixin,
                    mixins.RetrieveModelMixin,
                    viewsets.GenericViewSet):
    """
    Second version of products view but elastic search as a read database
    """
    permission_classes = ()
    lookup_field = 'id'
    pagination_class = ElasticLimitPagination
    filter_backends = (FullTextSearchFilter, ProductV2Filter)
    search_fields = (
        'title^3', 'description', 'location__title_ru^2', 'location__title_ky^2',
        'category__title_ru^2', 'category__title_ky^2'
    )
    ordering_fields = {'price': 'initial_price', 'upvote_date': 'upvote_date'}

    def get_serializer_class(self):
        if self.action == 'list':
            return serializers.ProductV2ListSerializer
        elif self.action == 'retrieve':
            return serializers.ProductV2DetailSerializer

    def set_ordering(self, queryset):
        ordering = self.request.query_params.get('ordering')
        if ordering:
            if ordering.startswith('-'):
                field = f"-{self.ordering_fields[ordering[1:]]}"
            else:
                field = self.ordering_fields[ordering]
            queryset = queryset.sort(field, 'id')
        else:
            queryset = queryset.sort('-upvote_date', 'id')
        return queryset

    def get_queryset(self):
        search_query = ProductDocument.search()
        search_query = search_query \
            .filter('term', state='active')
        search_query = self.set_ordering(search_query)
        return search_query

    def get_object(self):
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}
        obj = get_elastic_object_or_404(ProductDocument, **filter_kwargs)
        return obj

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(queryset=self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        async_task(update_both_view_count, instance, task_name='product-update-both-view-count')
        return Response(serializer.data)
