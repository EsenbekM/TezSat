import csv

from django.db.models import Count, Q
from django.http import HttpResponse
from rest_framework.generics import GenericAPIView

from .models import AdvertisementStatistics as AdStats


class StatisticsView(GenericAPIView):
    """
    Return attached statistics file
    """
    permission_classes = ()
    authentication_classes = ()
    serializer_class = None

    def get(self, request, *args, **kwargs):
        queryset = AdStats.objects.filter(advertisement__id=kwargs['id']).values('date')\
            .annotate(view_count=Count('type', filter=Q(type=AdStats.VIEW))) \
            .annotate(click_count=Count('type', filter=Q(type=AdStats.CLICK)))

        response = HttpResponse(content_type='text/csv')
        writer = csv.writer(response)
        writer.writerow(['date', 'view_count', 'click_count'])
        writer.writerows([[i['date'], i['view_count'], i['click_count']] for i in queryset])

        response['Content-Disposition'] = f'attachment; filename="{kwargs["id"]}-stats.csv"'

        return response
