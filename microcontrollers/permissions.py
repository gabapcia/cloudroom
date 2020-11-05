import base64
from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import BasePermission
from cloudroom.decorators import false_on_exception
from .models import Board


class BoardPermission(BasePermission):
    message = 'Credentials not provied'

    @false_on_exception
    def has_permission(self, request, view):
        auth = request.headers.get('Authorization', '')
        if not auth:
            return False

        auth = base64.b64decode(auth.encode('utf-8')).decode('utf-8')
        id, secret = auth[0], auth[1:]

        board = Board.objects.get(pk=id)

        board.verify_secret(secret=secret)

        request.board = board
        return True

    @false_on_exception
    def has_object_permission(self, request, view, obj):
        return request.board.pk == obj.pk
