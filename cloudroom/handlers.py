from rest_framework.views import exception_handler
from rest_framework.status import HTTP_400_BAD_REQUEST
from rest_framework.response import Response
from django.db.utils import IntegrityError
from django.core.exceptions import ValidationError


def handle_exceptions(exc, context):
    response = exception_handler(exc, context)

    if not response:
        if isinstance(exc, IntegrityError):
            msg = (
                'It seems there is a conflict between the data you are '
                'trying to save and your current data. '
                'Please review your entries and try again.'
            )
            response = Response({'detail': msg}, status=HTTP_400_BAD_REQUEST)
        elif isinstance(exc, ValidationError):
            response = Response({'detail': exc.args}, HTTP_400_BAD_REQUEST)

    return response
