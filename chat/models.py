from django.db import models
from django.contrib.auth import get_user_model
import os
from tezsat.utils import get_filename, compress_image
from .settings import PHOTO_UPLOAD_DIR
from copy import deepcopy

User = get_user_model()


class ChatManager(models.Manager):
    def get_chats(self, participants):
        return super().filter(models.Q(buyer=participants[0], seller=participants[1]) |
                              models.Q(buyer=participants[1], seller=participants[0]))


class Chat(models.Model):
    class Meta:
        db_table = 'chat'
    objects = ChatManager()
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, null=False, related_name='sender_chats')
    seller = models.ForeignKey(User, on_delete=models.CASCADE, null=False, related_name='receiver_chats')
    product = models.ForeignKey('product.Product', on_delete=models.CASCADE, null=False)
    creation_date = models.DateTimeField(auto_now_add=True)
    last_message_date = models.DateTimeField(null=False)
    last_message = models.TextField(null=False)


def photo_upload_to(instance, filename):
    new_filename = get_filename(filename)
    return os.path.join(PHOTO_UPLOAD_DIR, new_filename)


class ChatPhoto(models.Model):
    class Meta:
        db_table = 'chat_photo'

    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, null=False, related_name='photos')
    photo = models.ImageField('photo', upload_to=photo_upload_to, null=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.photo_ = deepcopy(self.photo)

    def save(self, *args, **kwargs):
        if self.photo and self.photo != self.photo_:
            self.photo = compress_image(self.photo)
        super().save(*args, **kwargs)
