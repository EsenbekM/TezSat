from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from .models import User


class CustomUserCreationForm(UserCreationForm):

    class Meta(UserCreationForm):
        model = User
        fields = ('name', 'email', 'phone', 'is_active', 'is_superuser', 'photo', 'fcm_id', 'location')


class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = User
        fields = ('name', 'email', 'phone', 'is_active', 'is_superuser', 'photo', 'fcm_id', 'location')
