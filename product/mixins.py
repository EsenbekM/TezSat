from django_q.tasks import async_task
from rest_framework import status
from rest_framework.response import Response
from category.models import Category
from category.serializers import CategoryV2GetParentsSerializer
from tezsat.utils import get_parent_ids, get_parent_
from .jobs import update_show_count, update_view_count


class ListModelStatsMixin:
    """
    List a queryset with background stats update.
    """
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            # async_task(update_show_count, page, task_name='product-update-show-count')
            update_show_count(page)
            return self.get_paginated_response(serializer.data)
        # async_task(update_show_count, queryset, task_name='product-update-show-count')
        update_show_count(queryset)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class RetrieveModelStatsMixin:
    """
    Retrieve a model instance.
    """
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        async_task(update_view_count, instance, task_name='product-update-view-count')
        serializer = self.get_serializer(instance)
        parents_list = list(get_parent_(instance.category, []))
        parents_list.reverse()
        new_dict = {'parents': parents_list}
        new_dict.update(serializer.data)
        return Response(data=new_dict, status=status.HTTP_200_OK)
