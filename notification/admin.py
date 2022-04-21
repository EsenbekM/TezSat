from django.contrib import admin

from . import models


@admin.register(models.PushNotification)
class PushNotificationAdmin(admin.ModelAdmin):
    list_display = ('title_ru', 'title_ky', 'location', 'creation_date',)
    list_filter = ('location',)
    readonly_fields = ('creation_date',)
    fieldsets = (
        (None,
         {'fields': (
             'title_ru', 'title_ky', 'message_ru', 'message_ky', 'location',
             'user_chunk', 'minutes', 'business', 'creation_date')}),
    )
    search_fields = ('title_ru', 'title_ky',)
    ordering = ('creation_date',)
    filter_horizontal = ()
    list_display_links = list_display
    raw_id_fields = ('location',)
