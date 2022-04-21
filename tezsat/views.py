from rest_framework.views import exception_handler as default_exception_handler, set_rollback
from rest_framework.response import Response
from django.core.exceptions import PermissionDenied
from django.http import Http404
from rest_framework import exceptions, settings
from django.shortcuts import render


def privacy_policy_ru(request):
    return render(request, 'privacy_policy_ru.html')


def privacy_policy_ky(request):
    return render(request, 'privacy_policy_ky.html')


def manual_ru(request):
    return render(request, 'manual_ru.html')


def manual_ky(request):
    return render(request, 'manual_ky.html')


def business_ru(request):
    return render(request, 'business_ru.html')


def business_ky(request):
    return render(request, 'business_ky.html')


def exception_handler(exc, context):
    response = normalize_exception(exc, context)
    # if response is not None:
    #     response.data['status_code'] = response.status_code

    return response


_non_field_error_key = settings.api_settings.NON_FIELD_ERRORS_KEY


def normalize_exception(exc, context):
    if isinstance(exc, Http404):
        exc = exceptions.NotFound()
    elif isinstance(exc, PermissionDenied):
        exc = exceptions.PermissionDenied()

    if isinstance(exc, exceptions.APIException):
        headers = {}
        if getattr(exc, 'auth_header', None):
            headers['WWW-Authenticate'] = exc.auth_header
        if getattr(exc, 'wait', None):
            headers['Retry-After'] = '%d' % exc.wait

        if isinstance(exc.detail, dict):
            data = exc.get_full_details()
        else:
            d = exc.get_full_details()
            if not isinstance(d, list):
                d = [d]
            data = {_non_field_error_key: d}

        set_rollback()
        return Response(data, status=exc.status_code, headers=headers)

    return None
