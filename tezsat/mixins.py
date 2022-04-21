from product.models import Product
from .utils import get_children_id


class ActionSerializerClassMixin(object):
    action_serializer_class = {}

    def get_serializer_class(self):
        if self.action_serializer_class and self.action in self.action_serializer_class:
            return self.action_serializer_class[self.action]
        return super(ActionSerializerClassMixin, self).get_serializer_class()


class ActionPermissionsMixin(object):
    action_permissions = {}

    def get_permissions(self):
        if self.action_permissions and self.action in self.action_permissions:
            return [permission() for permission in self.action_permissions[self.action]]
        return super(ActionPermissionsMixin, self).get_permissions()


class FilterByRecursion(object):
    def filter_children_ids(self, queryset, param, model):
        obj_str = self.request.GET.get(param)
        if not obj_str:
            return queryset
        raw_ids = []
        raw = obj_str.split(',')
        for id in raw:
            try:
                obj_id = int(id)
                raw_ids.append(obj_id)
            except Exception:
                return queryset
        ids = get_children_id(model, raw_ids)
        field = {
            f'{param}_id__in': ids
        }
        return queryset.filter(**field)
