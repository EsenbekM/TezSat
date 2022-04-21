from rest_framework import viewsets, mixins, decorators, response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from . import serializers, models


class NotificationView(mixins.RetrieveModelMixin,
                       mixins.UpdateModelMixin,
                       mixins.ListModelMixin,
                       mixins.DestroyModelMixin,
                       viewsets.GenericViewSet):
    serializer_class = serializers.NotificationSerializer

    def get_queryset(self):
        return models.Notification.objects.select_related('sender', 'receiver', 'product').filter(
            receiver=self.request.user).order_by('-creation_date')

    @decorators.action(['GET'], detail=False, authentication_classes=(JWTAuthentication,),
                       permission_classes=(IsAuthenticated,))
    def unread_count(self, request):
        unread_count = self.get_queryset().filter(is_read=False).count()
        return response.Response(data={
            "unread_count": unread_count
        })

    @decorators.action(['POST'], detail=False, authentication_classes=(JWTAuthentication,),
                       permission_classes=(IsAuthenticated,))
    def read_all(self, request):
        self.get_queryset().update(is_read=True)
        return response.Response()
