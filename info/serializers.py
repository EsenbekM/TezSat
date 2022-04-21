from rest_framework import serializers as s
from . import models


class InfoSerializer(s.ModelSerializer):
    class Meta:
        model = models.Info
        fields = ('app_version',)

