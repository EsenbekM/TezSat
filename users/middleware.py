from .models import User
from django.utils import timezone


def set_last_active_middleware(get_response):

    def middleware(request):
        response = get_response(request)
        if request.user.is_authenticated:
            User.objects.filter(pk=request.user.pk).update(last_active=timezone.now())
        return response
    return middleware

