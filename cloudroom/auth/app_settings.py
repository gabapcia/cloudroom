from .serializers import (
    JWTSerializer as DefaultJWTSerializer,
    LoginSerializer as DefaultLoginSerializer,
    UserDetailsSerializer as DefaultUserDetailsSerializer
) 
from django.conf import settings
from .utils import import_callable


serializers = getattr(settings, 'REST_AUTH_SERIALIZERS', {})

JWTSerializer = import_callable(
    serializers.get('JWT_SERIALIZER', DefaultJWTSerializer)
)

UserDetailsSerializer = import_callable(
    serializers.get('USER_DETAILS_SERIALIZER', DefaultUserDetailsSerializer)
)

LoginSerializer = import_callable(
    serializers.get('LOGIN_SERIALIZER', DefaultLoginSerializer)
)
