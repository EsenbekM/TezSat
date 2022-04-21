from django.utils import timezone


def update_lang_and_last_login(user, language):
    user.language = language
    user.last_login = timezone.now()
    user.save()


def update_last_login(user):
    user.last_login = timezone.now()
    user.save()


def update_sign_in_method(user, method):
    user.sign_in_method = method
    user.save()
