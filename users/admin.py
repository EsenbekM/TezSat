from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from django.db.models import Count
from django.utils.translation import gettext_lazy as _

from product.models import Product, Claim
from tezsat.admin import staff_admin
from .models import User


class ProductInlines(admin.TabularInline):
    model = Product
    fields = ('title', 'state', 'price_kgs', 'category', 'show_count', 'view_count')
    readonly_fields = fields
    extra = 0


class ClaimInline(admin.TabularInline):
    model = Claim
    fields = ('product', 'message', 'creation_date')
    readonly_fields = fields
    extra = 0


class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ('name', 'email', 'phone', 'is_active', 'product_count', 'sign_in_method')
    list_filter = ('is_active', 'is_superuser', 'location', 'sign_in_method', 'is_manager')
    list_editable = ('is_active',)
    readonly_fields = ('date_joined', 'last_login', 'product_count', 'last_active')
    fieldsets = (
        (None, {'fields': ('email', 'name', 'request_status', 'phone', 'password', 'photo', 'location', 'language', 'sign_in_method', 'balance', 'remove_layout')}),
        ('Dates', {'fields': ('date_joined', 'last_login', 'last_active')}),
        ('Restriction', {'fields': ('is_superuser', 'is_active', 'is_manager')}),
        ('Other', {'fields': ('fcm_id', 'firebase_uid')})
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'photo', 'location', 'password1', 'password2', 'is_active', 'is_manager')}
         ),
    )
    search_fields = ('email', 'name', 'phone')
    ordering = ('email',)
    filter_horizontal = ()
    list_display_links = ('name', 'email', 'phone',)
    raw_id_fields = ('location',)
    inlines = [ProductInlines, ClaimInline]

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            product_count=Count('products', distinct=True)
        )
        return queryset

    def product_count(self, obj):
        return obj.product_count

    product_count.admin_order_field = 'product_count'


admin.site.register(User, CustomUserAdmin)
admin.site.unregister(Group)

admin.site.site_header = _("TezSat Admin")


class StaffUserAdmin(CustomUserAdmin):

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


staff_admin.register(User, StaffUserAdmin)
