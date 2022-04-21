from django.utils import timezone
from rest_framework import serializers as s

from product.models import Product
from users.models import User
from . import models


class ChatSerializer(s.ModelSerializer):
    class Meta:
        model = models.Chat
        fields = '__all__'


class SendMessageSerializer(s.Serializer):
    user = s.IntegerField(required=True)
    product = s.IntegerField(required=True)
    message = s.CharField(required=True)

    def validate_user(self, user_id):
        user = User.objects.filter(id=user_id).first()
        if not user:
            raise s.ValidationError('user not found', 'not_found')
        return user

    def validate_product(self, product_id):
        product = Product.objects.filter(id=product_id).first()
        if not product:
            raise s.ValidationError('product not found', 'not_found')
        return product


class UploadImageSerializer(s.ModelSerializer):
    class Meta:
        model = models.ChatPhoto
        fields = ('id', 'chat', 'photo', 'user', 'product')
        read_only_fields = ('chat',)

    user = s.IntegerField(required=True, write_only=True)
    product = s.IntegerField(required=True, write_only=True)

    def validate(self, attrs):
        try:
            user = User.objects.get(pk=attrs['user'])
            product = Product.objects.get(pk=attrs['product'])
            attrs["user"] = user
            attrs["product"] = product
        except User.DoesNotExist or Product.DoesNotExist:
            raise s.ValidationError("no such user or product exists")

        return attrs

    def create(self, validated_data):
        participants = [self.context['request'].user, validated_data['user']]
        chat = models.Chat.objects.get_chats(participants).filter(product=validated_data['product']).first()
        if not chat:
            chat = models.Chat(buyer=self.context['request'].user, seller=validated_data['user'],
                               product=validated_data['product'])
            chat.last_message = "Photo"
            chat.last_message_date = timezone.now()
            chat.save()
        photo = models.ChatPhoto.objects.create(chat=chat, photo=validated_data['photo'])
        return photo
