from collections import OrderedDict

from django_q.tasks import async_task
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response

from product.jobs import update_both_show_count


class ElasticLimitPagination(LimitOffsetPagination):
    """
    Pagination of elastic search results
    """
    key_param = 'key'

    def get_key(self, request):
        try:
            return request.query_params[self.key_param]
        except (KeyError, ValueError):
            return ''

    def paginate_queryset(self, search_query, request, view=None):
        """
        Paginate search results with search_after and key value from frontend
        """
        self.limit = self.get_limit(request)
        self.key = self.get_key(request)

        if self.limit is None:
            return None

        self.offset = self.get_offset(request)
        self.request = request

        queryset = search_query.extra(size=self.limit)
        if self.key:
            queryset = queryset.extra(search_after=[*self.key.split(" ")])
        queryset = queryset.execute()

        try:
            if len(queryset.hits) < self.limit:
                self.new_key = None
            else:
                sort_values = queryset.hits.hits[-1]['sort']
                self.new_key = f"{sort_values[0]}+{sort_values[1]}" or None
        except IndexError:
            self.new_key = None

        self.count = queryset.hits.total.value
        async_task(update_both_show_count, queryset, task_name='product-update-both-show-count')

        if self.count == 0:
            return []

        return queryset.hits

    def get_next_key(self):
        if self.new_key == None:
            return None

        return self.new_key

    def get_previous_link(self):
        return None

    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('key', self.get_next_key()),
            ('results', data)
        ]))
