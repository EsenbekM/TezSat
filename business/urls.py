from django.urls import path, include
from rest_framework_nested import routers

from . import views

router = routers.SimpleRouter()
router.register('businesses', views.BusinessViewSet, 'businesses')
router.register('requests', views.BusinessRequestViewSet, 'requests')

business_many = routers.SimpleRouter()
business_many.register('branches', views.BusinessBranchesView, 'branches')
business_many.register('contacts', views.BusinessContactsView, 'contacts')
business_many.register('schedule', views.BusinessScheduleView, 'schedule')
business_many.register('banners', views.BusinessBannersView, 'banners')
business_many.register('reviews', views.ReviewsView, 'reviews')

extra_routes = routers.SimpleRouter()
extra_routes.register('catalog', views.BusinessCatalogView, 'catalog')
extra_routes.register('discounts', views.BusinessDiscountView, 'discounts')

urlpatterns = [
    path('v1/', include(router.urls)),
    path('v1/businesses/<int:pk>/', include(extra_routes.urls)),
    path('v1/profile/', views.BusinessApiView.as_view(), name='business-profile'),
    path('v1/profile/', include(business_many.urls)),
    path('v1/stats/all/', views.BusinessStatsApiView.as_view(), name='business-stats'),
    path('v1/stats/<int:pk>/', views.BusinessAdminStatsApiView.as_view(), name='business-stats'),
    path('v1/stats/products/<int:pk>/', views.BusinessProductsStatApiView.as_view(), name='business-products-stats'),
    path('v1/profile/deactivate/', views.DeactivateBusinessView.as_view()),
    path('v1/every_three_days/', views.EveryThreeDays.as_view()),
]
