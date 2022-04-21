from django.contrib import admin
from . import models


@admin.register(models.Info)
class InfoAdmin(admin.ModelAdmin):
    list_display = ('app_version',)
    list_display_links = list_display
