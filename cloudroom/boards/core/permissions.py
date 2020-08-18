import argon2, base64
from contextlib import suppress
from rest_framework.permissions import BasePermission
from ..models import Board
from ..utils.decorators import false_on_exception


class BoardPermission(BasePermission):
    message = 'Credentials not provied'

    @false_on_exception
    def has_permission(self, request, view):
        if not (auth := request.headers.get('Authentication', '')):
            return False

        auth = base64.b64decode(auth.encode('ascii')).decode('ascii')
        id, password = auth.split(' ')

        board = Board.objects.get(pk=id)

        ph = argon2.PasswordHasher()
        ph.verify(board.password, password)
        if ph.check_needs_rehash(board.password):
            board.password = ph.hash(password)
            board.save()
        request.board = board
        return True

    @false_on_exception
    def has_object_permission(self, request, view, obj):
        return request.board.pk == obj.pk
