from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from . import models

@admin.register(models.Advertisement)
class AdvertisementAdmin(admin.ModelAdmin):
    list_display = ('link', 'type', 'view_count', 'click_count', 'statistics')

    def statistics(self, obj):
        return format_html(
            '<a class="button" href="{}">Statistics</a>&nbsp;',
            reverse('ad-stats', args=[obj.pk])
        )

    statistics.short_description = 'Account Actions'
    statistics.allow_tags = True

admin.site.register(models.AdvertisementType)
