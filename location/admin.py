from django.contrib import admin
from adminsortable2.admin import SortableAdminMixin
from . import models
from .services import get_region_in_location


class LocationChildAdmin(admin.TabularInline):
    model = models.Location
    fields = ('type', 'title_ru', 'title_ky', 'request_ru', 'request_ky', 'lat', 'lng')
    extra = 0

def add_region(modeladmin, request, queryset):
    get_region_in_location()

add_region.short_description = "add region"

@admin.register(models.Location)
class LocationAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ('order', 'title_ru', 'title_ky', 'parent', 'type', 'region')
    list_display_links = list_display
    search_fields = ('title_ru', 'title_ky')
    inlines = (LocationChildAdmin,)
    raw_id_fields = ('parent',)
    list_filter = ('type', 'parent')

    fieldsets = (
        (None, {'fields': ('parent', 'type', 'title_ru', 'title_ky', 'region', 'request_ru', 'request_ky', 'lat', 'lng')}),
    )
    actions = [add_region]

