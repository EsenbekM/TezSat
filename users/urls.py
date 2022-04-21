from rest_framework.routers import DefaultRouter
from . import views
from django.urls import path, include
from rest_framework_simplejwt import views as jwt_views

router = DefaultRouter()
router.register('users', views.UsersView, 'users')

favorite_router = DefaultRouter()
favorite_router.register('categories', views.FavoriteCategory, 'categories')


urlpatterns = [
    path('v1/signup/', views.FirebaseSignUpView.as_view(), name='signup'),
    path('v1/login/', views.LoginView.as_view(), name='login'),
    path('v1/social_login/', views.SocialLoginView.as_view(), name='social_login'),
    path('v1/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    path('v1/verify/', jwt_views.token_verify),
    path('v1/profile/', views.ProfileApiView.as_view()),
    path('v1/profile/password/', views.PasswordView.as_view()),
    path('v1/profile/recovery/', views.PasswordRecoveryView.as_view()),
    path('v1/login_availability/', views.ExistenceView.as_view()),
    path('v1/registration_by_sms/', views.RegistrationBySMS.as_view()),
    path('v1/', include(router.urls)),
    path('v1/profile/', include(favorite_router.urls)),
]
