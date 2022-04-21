from django.db import models
from django.utils.translation import gettext_lazy as _

from .settings import LocationType


class Location(models.Model):
    class Meta:
        db_table = 'location'
        ordering = ('order',)

    type = models.CharField(_('type'), max_length=20, null=False, blank=False, choices=LocationType.choices(),
                            default=LocationType.COUNTRY)
    title_ru = models.CharField(_('title in russian'), max_length=50, null=False)
    title_ky = models.CharField(_('title in kyrgyz'), max_length=50, null=False)
    request_ru = models.CharField(_('request in russian'), max_length=100, null=True, blank=True, default='Выберите')
    request_ky = models.CharField(_('request in kyrgyz'), max_length=100, null=True, blank=True, default='Выберите')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    lat = models.DecimalField(_('latitude'), max_digits=9, decimal_places=6, null=False, blank=False,
                              default=LocationType.lat)
    lng = models.DecimalField(_('longitude'), max_digits=9, decimal_places=6, null=False, blank=False,
                              default=LocationType.lng)
    order = models.PositiveIntegerField(default=0, blank=False, null=False)
    region = models.CharField(_('region'), max_length=50, null=True, blank=True)    

    def _get_all_children(self, location, children):
        for child in location.children.all():
            child_children = {}
            self._get_all_children(child, child_children)
            children[child] = child_children if child_children else None

    def get_all_children(self):
        children = {}
        self._get_all_children(self, children)
        return children

    def __str__(self):
        return self.title_ru
        # return get_recursive_title(Location, self.id, 'ru')
