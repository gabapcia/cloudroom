from rest_framework.views import exception_handler
from rest_framework.status import HTTP_400_BAD_REQUEST
from rest_framework.response import Response
from django.db.utils import IntegrityError


def handle_exceptions(exc, context):
    response = exception_handler(exc, context)

    if not response:
        if isinstance(exc, IntegrityError):
            msg = (
                'The data provided is incompatible with this resource. '
                'Please review your entries and try again.'
            )
            response = Response({'detail': msg}, status=HTTP_400_BAD_REQUEST)

    return response
