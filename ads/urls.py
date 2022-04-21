from django.urls import path

from . import views

urlpatterns = [
    path('stats/<uuid:id>/', views.StatisticsView.as_view(), name='ad-stats')
]
