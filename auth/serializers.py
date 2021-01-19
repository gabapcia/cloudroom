from contextlib import suppress
from django.contrib.auth import authenticate, get_user_model
from django.utils.translation import gettext_lazy as _
from rest_framework import exceptions, serializers


UserModel = get_user_model()


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    password = serializers.CharField(style={'input_type': 'password'})

    def authenticate(self, **kwargs):
        return authenticate(self.context['request'], **kwargs)

    def validate(self, attrs):
        username = attrs.get('username')
        email = attrs.get('email')
        password = attrs.get('password')

        if not username and not email:
            msg = _('Must include either "username" or "email" and "password"')
            raise exceptions.ValidationError(msg)

        user = None

        if email:
            with suppress(UserModel.DoesNotExist):
                username = UserModel.objects.get(
                    email__iexact=email
                ).get_username()

        user = self.authenticate(username=username, password=password)

        if not user:
            msg = _('Unable to log in with provided credentials')
            raise exceptions.ValidationError(msg)

        attrs['user'] = user
        return attrs


class LogoutSerializer(serializers.Serializer):
    pass


class UserDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = ('username', 'email', 'first_name', 'last_name')
        read_only_fields = ('email', )


class JWTSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField()
    user = serializers.SerializerMethodField()

    def get_user(self, obj):
        return UserDetailsSerializer(
            obj['user'], context=self.context
        ).data
