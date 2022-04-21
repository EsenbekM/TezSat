from rest_framework import generics, response
from . import models, serializers


class InfoView(generics.GenericAPIView):
    permission_classes = ()
    authentication_classes = ()
    serializer_class = serializers.InfoSerializer

    def get(self, request):
        info = models.Info.objects.first()
        serializer = self.get_serializer(instance=info)
        return response.Response(data=serializer.data)
