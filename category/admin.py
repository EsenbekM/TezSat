from adminsortable2.admin import SortableAdminMixin
from django.contrib import admin
from django.utils.html import format_html

from tezsat.admin import staff_admin
from . import models
from .models import CategoryFixture


class CategoryChildInline(admin.TabularInline):
    model = models.Category
    fields = ('title_ru', 'title_ky', 'icon')
    extra = 0


class ParameterInline(admin.TabularInline):
    model = models.Parameter
    fields = ('type', 'title_ru', 'title_ky', 'optional', 'order')
    extra = 0


@admin.register(models.Category)
class CategoryAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ('order', 'title_ru', 'title_ky', 'title_slug', 'parent', 'order_id')
    list_display_links = ('title_ru',)
    search_fields = ('title_ru', 'title_ky')
    # ordering = ('parent', 'title_ru')
    inlines = (ParameterInline, CategoryChildInline,)
    raw_id_fields = ('parent',)
    list_filter = ('parent',)
    # list_editable = ('parent',)

    fieldsets = (
        (None, {'fields': ('parent', 'title_ru', 'title_ky', 'icon')}),
    )

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('parent')

    def order_id(self, obj):
        return obj.order

@admin.register(CategoryFixture)
class ParentsCategory(SortableAdminMixin, admin.ModelAdmin):
    list_display = ('order', 'title_ru', 'title_ky', 'title_slug', 'parent', 'order_id')
    list_display_links = ('title_ru',)
    inlines = (ParameterInline, CategoryChildInline,)
    raw_id_fields = ('parent',)
    list_filter = ('parent',)
    fieldsets = (
            (None, {'fields': ('parent', 'title_ru', 'title_ky', 'icon')}),
        )
    def order_id(self, obj):
        return obj.order

    def get_queryset(self, request):
        queryset = super(ParentsCategory, self).get_queryset(request)
        queryset = queryset.filter(parent__isnull=True)
        return queryset


class OptionsInline(admin.TabularInline):
    model = models.Option
    fields = ('title_ru', 'title_ky')
    extra = 0


@admin.register(models.Parameter)
class ParameterAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ('title_ru', 'is_many', 'title_ky', 'category', 'type')
    list_display_links = ('title_ru', 'title_ky', 'category', 'type')
    search_fields = ('title_ru', 'title_ky')
    list_filter = ('category',)
    inlines = (OptionsInline,)
    raw_id_fields = ('category',)
    list_editable = ('is_many', )


@admin.register(models.Option)
class OptionAdmin(admin.ModelAdmin):
    list_display = ('title_ru', 'title_ky', 'parameter')
    list_display_links = list_display
    search_fields = ('title_ru', 'title_ky')
    ordering = ('parameter',)
    raw_id_fields = ('parameter',)


class StaffCategoryChildInline(admin.TabularInline):
    model = models.Category
    fields = ("id", 'title_ru', 'title_ky', 'icon',)
    readonly_fields = ('title_ru', 'title_ky', 'icon')
    extra = 0

    def has_add_permission(self, request, *args, **kwargs):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class StaffCategoryAdmin(admin.ModelAdmin):
    """
    Class for managing categories from staff perspective
    """
    inlines = (StaffCategoryChildInline,)
    raw_id_fields = ('parent',)
    list_display = ('id', 'ru_title', 'ky_title', 'parent',)
    search_fields = ('title_ru', 'title_ky', 'parent__title_ru', 'parent__title_ky')
    list_display_links = ('id', 'ru_title')

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('parent')

    def ru_title(self, obj):
        try:
            if obj.title_ru == 'Другое':
                return format_html(f'{obj.title_ru} <b>&larr; {obj.parent.title_ru}</b>')
            return obj.title_ru
        except AttributeError:
            return obj.title_ru

    def ky_title(self, obj):
        try:
            if obj.title_ky == 'Башка':
                return format_html(f'{obj.title_ky} <b>&larr; {obj.parent.title_ky}</b>')
            return obj.title_ky
        except AttributeError:
            return obj.title_ky

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False


staff_admin.register(models.Category, StaffCategoryAdmin)
