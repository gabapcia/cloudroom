from datetime import datetime
from django.conf import settings
from django.contrib.auth import (
    get_user_model,
    login as django_login,
    logout as django_logout,
)
from django.core.exceptions import ObjectDoesNotExist
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.debug import sensitive_post_parameters
from rest_framework import status
from rest_framework.generics import GenericAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenViewBase
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.settings import api_settings as jwt_stgs

from .app_settings import (
    JWTSerializer, 
    LoginSerializer,
    UserDetailsSerializer,
)
from .utils import jwt_encode

sensitive_post_parameters_m = method_decorator(
    sensitive_post_parameters(
        'password', 'old_password', 'new_password1', 'new_password2'
    )
)


class TokenCookieRefreshView(TokenViewBase):
    serializer_class = TokenRefreshSerializer

    def post(self, request, *args, **kwargs):
        data = request.data.dict()
        if not data.get('refresh', None):
            data['refresh'] = request.COOKIES.get(
                settings.JWT_AUTH_REFRESH_COOKIE,
                ''
            )
        serializer = self.get_serializer(data=data)

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])

        return Response(serializer.validated_data, status=status.HTTP_200_OK)

class LoginView(GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = LoginSerializer

    @sensitive_post_parameters_m
    def dispatch(self, *args, **kwargs):
        return super(LoginView, self).dispatch(*args, **kwargs)

    def login(self):
        self.user = self.serializer.validated_data['user']
        self.access_token, self.refresh_token = jwt_encode(self.user)

        if getattr(settings, 'REST_SESSION_LOGIN', True):
            django_login(self.request, self.user)

    def get_response(self):
        data = {
            'user': self.user,
            'access_token': self.access_token,
            'refresh_token': self.refresh_token
        }
        serializer = JWTSerializer(
            instance=data,
            context=self.get_serializer_context()
        )

        response = Response(serializer.data, status=status.HTTP_200_OK)
        response.set_cookie(
            settings.JWT_AUTH_REFRESH_COOKIE,
            self.refresh_token,
            expires=(datetime.utcnow() + jwt_stgs.REFRESH_TOKEN_LIFETIME),
            secure=False,
            httponly=True,
            samesite='Lax'
        )
        return response

    def post(self, request, *args, **kwargs):
        self.request = request
        self.serializer = self.get_serializer(data=self.request.data)
        self.serializer.is_valid(raise_exception=True)

        self.login()
        return self.get_response()

class LogoutView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, *args, **kwargs):
        if getattr(settings, 'ACCOUNT_LOGOUT_ON_GET', False):
            response = self.logout(request)
        else:
            response = self.http_method_not_allowed(request, *args, **kwargs)

        return self.finalize_response(request, response, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.logout(request)

    def logout(self, request):
        try:
            request.user.auth_token.delete()
        except (AttributeError, ObjectDoesNotExist):
            pass

        if getattr(settings, 'REST_SESSION_LOGIN', True): django_logout(request)

        response = Response(
            {"detail": _("Successfully logged out.")},
            status=status.HTTP_200_OK
        )

        response.delete_cookie(settings.JWT_AUTH_REFRESH_COOKIE)

        return response

class UserDetailsView(RetrieveUpdateAPIView):
    serializer_class = UserDetailsSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user

    def get_queryset(self):
        """
        Adding this method since it is sometimes called when using
        django-rest-swagger
        """
        return get_user_model().objects.none()
