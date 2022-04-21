import datetime
import random

from django.contrib.auth import authenticate
from django.utils import timezone
from django_q.tasks import async_task
from drf_yasg2.utils import swagger_auto_schema
from rest_framework import generics, mixins, viewsets, status, response, exceptions
from rest_framework_simplejwt.tokens import RefreshToken

from business.models import BusinessPeriod
from category.serializers import ChildCategoryV2Serializer
from tezsat.mixins import ActionSerializerClassMixin
from . import jobs
from . import serializers as s, services
from .exceptions import UserAlreadyExist, UserNotFound
from .models import User, SMSCode
from .services import _send_to_the_code
from .settings import SignInMethods
from .utils import get_user_from_firebase


def get_login_response(user, request):
    refresh = RefreshToken.for_user(user)
    data = {
        "user": s.UserSerializer(instance=user, context={'request': request}).data,
        "refresh": str(refresh),
        "access": str(refresh.access_token)
    }
    return data


class LoginView(generics.GenericAPIView):
    authentication_classes = ()
    permission_classes = ()
    serializer_class = s.LoginSerializer

    @swagger_auto_schema(responses={'200': s.LoginResponseSerializer()}, tags=['auth'])
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(True)
        user = authenticate(login=serializer.validated_data['login'], password=serializer.validated_data['password'])
        if not user:
            raise exceptions.AuthenticationFailed()
        async_task(jobs.update_lang_and_last_login, user, serializer.validated_data['language'],
                   task_name='user-lang-and-last-login-update')
        jobs.update_sign_in_method(user, SignInMethods.credentials)
        return response.Response(data=get_login_response(user, request))


class SocialLoginView(generics.GenericAPIView):
    authentication_classes = ()
    permission_classes = ()
    serializer_class = s.SocialLoginSerializer

    @swagger_auto_schema(responses={'200': s.LoginResponseSerializer()}, tags=['auth'])
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = services.firebase_login(serializer.validated_data)
        return response.Response(data=get_login_response(user, request))


class FirebaseSignUpView(generics.GenericAPIView):
    authentication_classes = ()
    permission_classes = ()
    serializer_class = s.FirebaseSignUpSerializer

    @swagger_auto_schema(responses={'200': s.LoginResponseSerializer()}, tags=['auth'])
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(True)
        decoded = serializer.validated_data['decoded']
        params = get_user_from_firebase(decoded)
        if isinstance(params, User):
            raise UserAlreadyExist()
        user = User(**params, name=serializer.validated_data['name'], language=serializer.validated_data['language'])
        if params['sign_in_method'] == SignInMethods.credentials:
            if serializer.validated_data.get('password') is None:
                raise exceptions.ValidationError({'password': 'required'}, code='required')
            password = serializer.validated_data['password']
            user.set_password(password)
        user.last_login = timezone.now()
        user.save()

        return response.Response(data=get_login_response(user, request))


class UsersView(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    permission_classes = ()
    authentication_classes = ()
    serializer_class = s.PublicUserSerializer

    def get_queryset(self):
        return User.objects.all()


class ProfileApiView(generics.GenericAPIView):
    serializer_class = s.UserSerializer
    pagination_class = None

    @swagger_auto_schema(responses={'200': s.UserSerializer()}, tags=['auth'])
    def get(self, request):
        user = request.user
        if not user.remove_layout:
            user.remove_layout = BusinessPeriod.objects.last().end_date
            user.save()
        serializer = self.get_serializer(instance=request.user)
        return response.Response(data=serializer.data)

    def patch(self, request):
        serializer = self.get_serializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response.Response(data=serializer.data)


class PasswordView(generics.GenericAPIView):
    serializer_class = s.UpdatePasswordSerializer

    @swagger_auto_schema(responses={'200': ''}, tags=['auth'])
    def post(self, request):
        serializer = s.UpdatePasswordSerializer(data=request.data, instance=request.user, context={'request': request})
        serializer.is_valid(True)
        serializer.save()
        return response.Response(status=200)


class PasswordRecoveryView(generics.GenericAPIView):
    permission_classes = ()
    authentication_classes = ()
    serializer_class = s.PasswordRecoverySerializer

    @swagger_auto_schema(responses={'200': s.LoginResponseSerializer()}, tags=['auth'])
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(True)
        decoded = serializer.validated_data['decoded']
        password = serializer.validated_data['password']
        user = get_user_from_firebase(decoded)
        if not isinstance(user, User):
            raise UserNotFound()
        user.set_password(password)
        user.save()
        return response.Response(data=get_login_response(user, request))


class ExistenceView(generics.GenericAPIView):
    permission_classes = ()
    authentication_classes = ()
    serializer_class = s.ExistenceSerializer

    @swagger_auto_schema(responses={'200': ''}, tags=['auth'])
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(True)
        return response.Response(status=status.HTTP_200_OK)


class FavoriteCategory(ActionSerializerClassMixin,
                       mixins.CreateModelMixin,
                       mixins.ListModelMixin,
                       viewsets.GenericViewSet):
    serializer_class = s.FavoriteCategoryCreationSerializer
    action_serializer_class = {
        'list': ChildCategoryV2Serializer
    }

    def get_queryset(self):
        return self.request.user.categories.all()


class RegistrationBySMS(
    generics.GenericAPIView):
    permission_classes = ()
    authentication_classes = ()

    @swagger_auto_schema(responses={'200': ''}, tags=['auth'])
    def post(self, request):
        code = random.randint(100000, 999999)
        phone = request.data.get('phone')
        sms = SMSCode.objects.create(code=code, phone=phone)

        _send_to_the_code(id=sms.id, code=code, phone=phone)

        return response.Response(data={'code': code}, status=status.HTTP_200_OK)
