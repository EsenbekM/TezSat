from django.conf import settings as project_settings
from django.contrib import admin
from django.contrib.admin.models import LogEntry, DELETION
from django.db.models import Count, OuterRef, Subquery
from django.urls import reverse
from django.utils.html import escape, format_html
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from django_q.tasks import async_task
from rangefilter.filter import DateRangeFilter

from tezsat.admin import staff_admin
from . import models, settings
from .jobs import change_state
from .models import ProductReview

MEDIA_URL = project_settings.MEDIA_URL


def make_activated(modeladmin, request, queryset):
    async_task(change_state, settings.ProductState.ACTIVE, queryset, task_name='update-product-state-elastic')


def make_blocked(modeladmin, request, queryset):
    async_task(change_state, settings.ProductState.BLOCKED, queryset, task_name='update-product-state-elastic')


make_activated.short_description = "Mark selected products as active"
make_blocked.short_description = "Mark selected products as blocked"


class ProductContactInline(admin.TabularInline):
    model = models.ProductContact
    fields = ('phone',)
    extra = 0


class ProductPhotoInline(admin.TabularInline):
    model = models.ProductPhoto
    fields = ('photo', 'image')
    extra = 0
    readonly_fields = ('image',)

    def image(self, obj):
        return format_html(f'<img loading="lazy" src="{obj.medium_thumbnail.url}" height="320px" width="auto"/>')


class ClaimInline(admin.TabularInline):
    model = models.Claim
    fields = ('user', 'message', 'creation_date')
    readonly_fields = fields
    extra = 0


class ReviewInline(admin.TabularInline):
    model = models.ProductReview
    fields = ('user', 'rating', 'review', 'creation_date', 'response', 'response_date', 'claim', 'claim_date')
    readonly_fields = fields
    extra = 0


class ProductParameterInline(admin.TabularInline):
    model = models.ProductParameter
    fields = ('parameter', 'option', 'response')
    raw_id_fields = ('parameter', 'option')
    extra = 0
    # fieldsets = (
    #     (None, {'fields': ('parameter',)}),
    # )

    # def get_queryset(self, request):
    #     print('here')
    #     return super().get_queryset(request)

    # def formfield_for_foreignkey(self, db_field, request, **kwargs):
    #     print(dir(self))
    #     print(db_field, kwargs)
    #     if db_field.name == 'parameter':
    #         print(dir(self.parent_model.category))
    #         # category = self.parent_model.category.get_object()
    #         # print(category, type(category))
    #     if db_field.name == 'option':
    #         print(kwargs)
    #         kwargs['queryset'] = Option.objects.filter(title_ru__in=['a'])
    #     return super().formfield_for_foreignkey(db_field, request, **kwargs)


# class FavoriteInline(admin.TabularInline):
#     model = models.Favorite
#     fields = ('user', 'creation_date')
#     readonly_fields = ('creation_date',)
#     raw_id_fields = ('user',)


@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    date_hierarchy = 'creation_date'
    list_display = ('photo', 'title_', 'state', 'price_kgs', 'category', 'creation_date', 'claim_count',
                    'show_count', 'view_count', 'favorite_count', 'rating')
    list_display_links = ()
    list_filter = ('state', ('creation_date', DateRangeFilter))
    search_fields = ('title', 'description')
    inlines = (ProductContactInline, ProductPhotoInline, ProductParameterInline, ClaimInline, ReviewInline)
    list_editable = ('state', 'category')
    readonly_fields = ('price_kgs', 'price_usd', 'upvote_date', 'creation_date', 'show_count', 'view_count',
                       'rating', 'call_count', 'message_count')
    raw_id_fields = ('user', 'category')
    # sortable_by = 'creation_date'

    fieldsets = (
        (_('General'), {'fields': (
            'user', 'description', 'state', 'category', 'location',
            'currency', 'initial_price', 'price_kgs', 'price_usd', 'discount',
            'discount_price_kgs', 'discount_price_usd',
            'creation_date', 'upvote_date', 'show_count', 'view_count', 'rating', 'rating_disabled',
            'call_count', 'message_count'
        )}),
    )
    actions = (make_activated, make_blocked)

    def get_queryset(self, request):
        photo_qs = models.ProductPhoto.objects.filter(product=OuterRef('pk')).values('small_thumbnail')
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            favorite_count=Count('favorites', distinct=True),
            claim_count=Count('claims', distinct=True),
            photo=Subquery(photo_qs[:1])
        ).select_related('category')
        return queryset.order_by('-creation_date')

    def title_(self, obj):
        info = obj._meta.app_label, obj._meta.model_name
        url = reverse('admin:%s_%s_change' % info, args=(obj.pk,))
        if hasattr(obj.user, 'business'):
            return format_html(f"""
            <a href="{url}" style="color: blue;">{obj.title}</a>
            """)
        return format_html(f"""
            <a href="{url}">{obj.title}</a>
            """)

    def favorite_count(self, obj):
        return obj.favorite_count

    def claim_count(self, obj):
        return obj.claim_count

    def photo(self, obj):
        if obj.photo:
            url = f"{MEDIA_URL}{obj.photo}"
            return format_html(f'<img src="{url}" width=auto height=100 />')
        return '-'

    favorite_count.admin_order_field = 'favorite_count'
    claim_count.admin_order_field = 'claim_count'
    photo.admin_order_field = 'photo'


@admin.register(models.Keyword)
class KeywordAdmin(admin.ModelAdmin):
    list_display = ('keyword', 'is_search')

    def get_queryset(self, request):
        return self.model.objects.filter(is_search=True)


@admin.register(models.Rate)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ('currency', 'rate', 'last_update')
    list_display_links = list_display
    readonly_fields = ('last_update',)


@admin.register(models.Claim)
class ClaimAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'creation_date', 'type', 'message')
    list_display_links = list_display
    raw_id_fields = ('product', "user")
    readonly_fields = ("message", "creation_date")
    fieldsets = (
        (_('Product'), {"fields": ("product", "user", "creation_date", 'type', "message")}),
    )

@admin.register(models.ReviewClaimProxy)
class ClaimReviewAdmin(admin.ModelAdmin):
    list_display = ('review', 'rating', 'claim', 'claim_date')
    list_display_links = list_display
    fieldsets = (
        (None, {'fields': ('product',)}),
        ('Review', {"fields": ("user", "review", 'rating')}),
        ('Claim', {"fields": ("claim", 'claim_date')})
    )
    raw_id_fields = ('product',)
    readonly_fields = ('user', 'review', 'claim', 'claim_date', 'rating',)

    def get_queryset(self, request):
        claims = ProductReview.objects.filter(claim__isnull=False)
        return claims

@admin.register(models.ClaimCategory)
class ClaimCategoryAdmin(admin.ModelAdmin):
    list_display =  ('icon', 'claim_type', 'language')
    list_display_links = list_display
    fieldsets = (
        (None, {"fields": ("icon", "claim_type", 'language')}),
    )


class ClaimFilter(admin.SimpleListFilter):
    title = _('claim')
    parameter_name = 'claim'

    def lookups(self, request, model_admin):
        return (
            ('yes', _('reviews have claim')),
            ('no', _('reviews do not have claim'))
        )

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.filter(claim__isnull=False)
        elif self.value() == 'no':
            return queryset.filter(claim__isnull=True)
        else:
            return queryset


@admin.register(models.ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'product', 'user', 'rating', 'review', 'response', 'claim', 'creation_date', 'response_date', 'claim_date', 'is_read'
    )
    list_display_links = list_display
    readonly_fields = list_display
    raw_id_fields = ('product', 'user')
    list_filter = (ClaimFilter,)


# @admin.register(models.ProductContact)
# class ProductContactAdmin(admin.ModelAdmin):
#     list_display = ('product', 'phone')
#     list_display_links = list_display
#
#
# @admin.register(models.ProductPhoto)
# class ProductPhotoAdmin(admin.ModelAdmin):
#     list_display = ('product', 'photo')
#     list_display_links = list_display
#
#
# @admin.register(models.ProductParameter)
# class ProductParameterAdmin(admin.ModelAdmin):
#     list_display = ('product', 'parameter', 'option')
#     list_display_links = list_display
#     raw_id_fields = ('product', 'parameter', 'option')


# @admin.register(models.Favorite)
# class FavoriteAdmin(admin.ModelAdmin):
#     list_display = ('product', 'user')
#     list_display_links = list_display


class StaffProductAdmin(admin.ModelAdmin):
    search_fields = ('title', 'description', 'user__name', 'user__email', 'user__phone')
    list_display_links = ('photo',)
    list_filter = ('state',)
    list_display = (
        'photo', 'title', 'state', 'price_kgs', 'category', 'creation_date',
        'show_count', 'view_count', 'rating', 'favorite_count',
    )
    readonly_fields = ('price_kgs', 'price_usd', 'upvote_date', 'creation_date', 'show_count', 'view_count',
                       'rating', 'call_count', 'message_count')
    list_editable = ('title', 'state', 'category')
    raw_id_fields = ('user', 'category',)
    fieldsets = (
        (_('General'), {'fields': (
            'user', 'description', 'state', 'category', 'location',
            'currency', 'initial_price', 'price_kgs', 'price_usd',
            'creation_date', 'upvote_date', 'show_count', 'view_count', 'rating', 'rating_disabled',
            'call_count', 'message_count'
        )}),
    )
    inlines = (ProductContactInline, ProductPhotoInline)
    actions = (make_activated, make_blocked)

    def get_queryset(self, request):
        photo_qs = models.ProductPhoto.objects.filter(product=OuterRef('pk')).values('small_thumbnail')
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            favorite_count=Count('favorites', distinct=True),
            claim_count=Count('claims', distinct=True),
            photo=Subquery(photo_qs[:1])
        ).select_related('category')

        return queryset.order_by('-creation_date')

    def favorite_count(self, obj):
        return obj.favorite_count

    def claim_count(self, obj):
        return obj.claim_count

    def photo(self, obj):
        if obj.photo:
            url = f"{MEDIA_URL}{obj.photo}"
            return format_html(f'<img loading="lazy" src="{url}" width=auto height=100 />')
        return '-'

    def has_delete_permission(self, request, obj=None):
        return True

    favorite_count.admin_order_field = 'favorite_count'
    claim_count.admin_order_field = 'claim_count'
    photo.admin_order_field = 'photo'


staff_admin.register(models.Product, StaffProductAdmin)


@admin.register(LogEntry)
class LogEntryAdmin(admin.ModelAdmin):
    date_hierarchy = 'action_time'

    list_filter = [
        'content_type',
        'action_flag'
    ]

    search_fields = [
        'object_repr',
        'change_message',
        'user__name',
    ]

    list_display = [
        'action_time',
        'user',
        'content_type',
        'object_link',
        'action_flag',
    ]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def object_link(self, obj):
        if obj.action_flag == DELETION:
            link = escape(obj.object_repr)
        else:
            ct = obj.content_type
            link = '<a href="%s">%s</a>' % (
                reverse('admin:%s_%s_change' % (ct.app_label, ct.model), args=[obj.object_id]),
                escape(obj.object_repr),
            )
        return mark_safe(link)

    def get_queryset(self, request, *args, **kwargs):
        queryset = super(LogEntryAdmin, self).get_queryset(request, *args, **kwargs)
        return queryset.select_related('user')

    object_link.admin_order_field = "object_repr"
    object_link.short_description = "object"
