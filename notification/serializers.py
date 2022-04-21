from rest_framework import serializers as s
from . import models
from users.serializers import PublicUserSerializer
from product.serializers import ShortProductSerializer, NakedProductSerializer
from product.models import Product, ProductPhoto
from django.db.models import OuterRef, Count, Subquery


class NotificationSerializer(s.ModelSerializer):
    class Meta:
        model = models.Notification
        fields = ('id', 'sender', 'receiver', 'action', 'product', 'creation_date', 'is_read', 'title_ky', 'description_ky',
                  'title_ru', 'description_ru')
        read_only_fields = ('id', 'sender', 'receiver', 'action', 'product', 'creation_date')

    sender = PublicUserSerializer(read_only=True)
    receiver = PublicUserSerializer(read_only=True)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        serializer = None
        if instance.product:
            photo_qs = ProductPhoto.objects.filter(product=OuterRef('pk')).values('photo')
            product = Product.objects.filter(id=instance.product_id).annotate(favorite_count=Count('favorites'), photo=Subquery(photo_qs[:1])).first()
            serializer = NakedProductSerializer(instance=product, context=self.context).data
        data['product'] =  serializer
        return data

