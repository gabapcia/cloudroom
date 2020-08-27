import base64
from rest_framework.permissions import BasePermission
from ..models import Board
from ..utils.decorators import false_on_exception


class BoardPermission(BasePermission):
    message = 'Credentials not provied'

    @false_on_exception
    def has_permission(self, request, view):
        auth = request.headers.get('Authorization', '')
        if not auth:
            return False

        auth = base64.b64decode(auth.encode('ascii')).decode('ascii')
        id, password = auth.split(' ')

        board = Board.objects.get(pk=id)

        board.verify_password(password=password)

        request.board = board
        return True

    @false_on_exception
    def has_object_permission(self, request, view, obj):
        return request.board.pk == obj.pk
