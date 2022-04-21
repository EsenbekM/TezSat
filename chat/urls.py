from rest_framework.routers import DefaultRouter
from . import views
from django.urls import path, include


router = DefaultRouter()
router.register('chats', views.ChatView, 'chats')

urlpatterns = [
    path('v1/send_message/', views.SendMessageView.as_view()),
    path('v1/upload_photo/', views.UploadImage.as_view()),
    # path('v1/', include(router.urls)),
]
