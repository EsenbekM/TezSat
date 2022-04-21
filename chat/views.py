from django_q.tasks import async_task
from drf_yasg2.utils import swagger_auto_schema
from rest_framework import response, viewsets, generics

from . import jobs
from .models import Chat
from .serializers import SendMessageSerializer, ChatSerializer, UploadImageSerializer


class ChatView(viewsets.ReadOnlyModelViewSet):
    serializer_class = ChatSerializer

    def get_queryset(self):
        return Chat.objects.get_chats([self.request.user]).all()


class SendMessageView(generics.GenericAPIView):
    serializer_class = SendMessageSerializer

    @swagger_auto_schema(responses={'200': ''}, tags=['chat'])
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        message = serializer.validated_data['message']
        product = serializer.validated_data['product']
        async_task(jobs.new_message, self.request.user, user, product, message, task_name='chat-new-message')
        return response.Response()


class UploadImage(generics.GenericAPIView):
    serializer_class = UploadImageSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response.Response(data=serializer.data)
