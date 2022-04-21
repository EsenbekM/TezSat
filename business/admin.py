from django.contrib import admin

from django.contrib.admin import SimpleListFilter
from django.utils.html import format_html

from users.settings import RequestStatuses
from . import models
from .jobs import denied_push
from .models import BusinessPeriod


class ContactInline(admin.TabularInline):
    model = models.BusinessContact
    fields = ('type', 'value')
    extra = 0


class ScheduleInline(admin.TabularInline):
    model = models.BusinessSchedule
    fields = ('weekday', 'time')
    extra = 0


class BranchInLine(admin.TabularInline):
    model = models.BusinessBranch
    fields = ('address', 'lat', 'lng')
    extra = 0


class BannerInLine(admin.TabularInline):
    model = models.BusinessBanner
    fields = ('photo', 'text')
    extra = 0


def make_published_denied(modeladmin, request, queryset):
    denied_push(queryset)


make_published_denied.short_description = "Cancel Selected Ones"


class CatalogInline(admin.TabularInline):
    model = models.BusinessCatalog
    fields = ("name", "products")
    extra = 0


class BusinessFilter(SimpleListFilter):
    title = 'Business Filter'

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'data'

    def lookups(self, request, model_admin):
        return (
            (2, 'is_active'),
            (1, 'status_on_review'),
            (0, 'denied'),
        )

    def queryset(self, request, queryset):
        result = self.used_parameters
        if result:
            if result['data'] == '2':
                return queryset.filter(is_active=True)
            elif result['data'] == '1':
                return queryset.filter(user__request_status=RequestStatuses.ON_REVIEW)
            else:
                return queryset.filter(denied=True)
        return queryset


@admin.register(models.Business)
class BusinessAdmin(admin.ModelAdmin):
    list_display = (
    'user', 'name', 'is_active', 'get_description', 'product_limit', 'is_not_demo', 'category', 'creation_date', 'rating',
    'upvote_count')
    list_display_links = ('user', 'name', 'category', 'creation_date', 'rating',)
    search_fields = ('user__name', 'name', 'description', 'category__title_ky', "category__title_ru")
    ordering = ('creation_date',)
    raw_id_fields = ('user', 'category')
    list_editable = ('product_limit', 'upvote_count', 'is_active', 'is_not_demo')
    list_filter = ('is_active', BusinessFilter)

    change_form_template = 'admin/business-stats.html'
    fieldsets = (
        (None,
         {'fields': ('user', 'name', 'description', 'is_active', 'banner', 'category', 'product_limit', 'creation_date',
                     'rating', 'upvote_count', 'deactivate_date', 'is_not_demo')}),
        ('Messages', {'fields': ('message', 'deactivation_message')})
    )
    readonly_fields = ('creation_date', 'rating')
    inlines = (ContactInline, ScheduleInline, BranchInLine, BannerInLine)

    actions = [make_published_denied]

    def get_description(self, obj):
        return format_html(f"""
            <textarea name="message" placeholder="Business description" readonly="readonly">{obj.description}</textarea>
        """)

@admin.register(models.AddModal)
class AddModalAdmin(admin.ModelAdmin):
    list_display = ("name", 'date')


@admin.register(BusinessPeriod)
class BusinessPeriodAdmin(admin.ModelAdmin):
    list_display = ('id', 'period_name', 'end_date',)