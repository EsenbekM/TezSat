from django.urls import path, include
from rest_framework import routers

from . import views

router = routers.SimpleRouter()
router.register('products', views.ProductViewV2, 'products-v2')

urlpatterns = [
    path('', include(router.urls)),
    path('suggestions/', views.SuggestionsView.as_view(), name='suggestions'),
]
