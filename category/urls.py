from rest_framework.routers import DefaultRouter
from . import views
from django.urls import path, include


router = DefaultRouter()
router.register('categories', views.CategoryView, 'categories')

router_v2 = DefaultRouter()
router_v2.register('categories', views.CategoryV2View, 'categories_v2')

urlpatterns = [
    path('v1/', include(router.urls)),
    path('v2/', include(router_v2.urls))
]
