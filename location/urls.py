from rest_framework.routers import DefaultRouter
from . import views
from django.urls import path, include


router = DefaultRouter()
router.register('locations', views.LocationView, 'locations')

urlpatterns = [
    path('v1/', include(router.urls))
]
