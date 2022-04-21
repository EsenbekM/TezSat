from django.http import Http404
from elasticsearch.exceptions import NotFoundError


def get_elastic_object_or_404(document, **kwargs):
    try:
        obj = document.get(**kwargs)
        if obj.state != 'active':
            raise NotFoundError
        return obj
    except NotFoundError:
        raise Http404
