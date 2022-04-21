"""tezsat URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import debug_toolbar
from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from drf_yasg2 import openapi
from drf_yasg2.views import get_schema_view
from rest_framework import permissions

from . import views
from .admin import staff_admin

schema_view = get_schema_view(
    openapi.Info(
        title="TezSat API",
        default_version='v1',
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('jet/dashboard/', include('jet.dashboard.urls', 'jet-dashboard')),
    path('jet/', include('jet.urls', 'jet')),  # Django JET URLS
    path('admin/', admin.site.urls),
    path('staff-admin/', staff_admin.urls),
    path('auth/', include('users.urls')),
    path('location/', include('location.urls')),
    path('category/', include('category.urls')),
    path('product/', include('product.urls')),
    path('chat/', include('chat.urls')),
    path('notification/', include('notification.urls')),
    path('policy', views.privacy_policy_ru),
    path('policy/ru', views.privacy_policy_ru),
    path('policy/ky', views.privacy_policy_ky),
    path('manual/ru', views.manual_ru),
    path('manual/ky', views.manual_ky),
    path('business/ru', views.business_ru),
    path('business/ky', views.business_ky),
    path('business/', include('business.urls')),
    path('info/', include('info.urls')),
    path('ads/', include('ads.urls')),
    path('payment/', include('payment.urls')),
]

if settings.DEBUG:
    urlpatterns += [
        path('swagger.json', schema_view.without_ui(cache_timeout=0), name='schema-json'),
        path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
        path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
        path('__debug__/', include(debug_toolbar.urls)),
    ]
