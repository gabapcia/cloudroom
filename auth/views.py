from datetime import datetime
from django.conf import settings
from django.contrib.auth import get_user_model, login, logout
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.decorators import action
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.settings import api_settings as jwt_stgs
from .serializers import (
    JWTSerializer,
    LoginSerializer,
    LogoutSerializer,
    UserDetailsSerializer,
)


class AuthViewSet(GenericViewSet):
    queryset = get_user_model().objects.none()

    def get_serializer_class(self):  # pragma: no cover
        serializers = {
            'me': UserDetailsSerializer,
            'login': LoginSerializer,
            'refresh': TokenRefreshSerializer,
            'logout': LogoutSerializer,
        }
        return serializers.get(self.action)

    @action(methods=['GET'], detail=False)
    def me(self, request):
        user = request.user
        data = UserDetailsSerializer(
            user,
            context=self.get_serializer_context(),
        ).data
        return Response(data)

    @action(methods=['POST'], detail=False)
    def logout(self, request):
        try:
            request.user.auth_token.delete()
        except (AttributeError, ObjectDoesNotExist):
            pass

        if getattr(settings, 'REST_SESSION_LOGIN', True):
            logout(request)

        response = Response(status=status.HTTP_204_NO_CONTENT)
        response.delete_cookie(settings.JWT_AUTH_REFRESH_COOKIE)

        return response

    @action(methods=['POST'], detail=False, permission_classes=[AllowAny])
    def login(self, request):
        serializer = LoginSerializer(
            data=request.data,
            context=self.get_serializer_context(),
        )
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']
        refresh_token = TokenObtainPairSerializer.get_token(user)
        access_token = refresh_token.access_token

        if getattr(settings, 'REST_SESSION_LOGIN', True):
            login(request, user)

        data = {
            'user': user,
            'access': access_token,
            'refresh': refresh_token,
        }
        serializer = JWTSerializer(data, context=self.get_serializer_context())

        response = Response(serializer.data)
        response.set_cookie(
            settings.JWT_AUTH_REFRESH_COOKIE,
            refresh_token,
            expires=(datetime.utcnow() + jwt_stgs.REFRESH_TOKEN_LIFETIME),
            secure=False,
            httponly=True,
            samesite='Lax'
        )
        return response

    @action(methods=['POST'], detail=False, permission_classes=[AllowAny])
    def refresh(self, request):
        data = dict(request.data)

        if not data.get('refresh'):
            refresh_cookie_name = settings.JWT_AUTH_REFRESH_COOKIE
            data['refresh'] = request.COOKIES.get(refresh_cookie_name, '')

        serializer = TokenRefreshSerializer(data=data)

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])

        return Response(serializer.validated_data)
