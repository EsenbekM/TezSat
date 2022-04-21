from rest_framework.routers import DefaultRouter
from . import views
from django.urls import path, include


urlpatterns = [
    path('v1/info/', views.InfoView.as_view(), name='info'),
]
