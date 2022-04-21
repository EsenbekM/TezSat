from django.urls import path, include
from rest_framework_nested import routers

from . import views
from .v2 import urls as urls_v2

router = routers.SimpleRouter()
router.register('currencies', views.CurrencyView, 'currencies')
router.register('products/claim', views.ProductClaimView, 'claim')
router.register('products', views.ProductView, 'products')
router.register('personal/products', views.PersonalProductView, 'personal_products')
router.register('personal/photo-upload', views.PhotoUploadView, 'photo_upload')
router.register('personal/favorites', views.FavoriteView, 'favorites')
router.register('personal/likes', views.LikeView, 'likes')

review_router = routers.NestedSimpleRouter(router, 'products', lookup='product')
review_router.register('reviews', views.ProductReviewView, 'product_reviews')

urlpatterns = [
    path('v1/', include(router.urls)),
    path('v1/', include(review_router.urls)),
    path('v2/', include(urls_v2)),
]
