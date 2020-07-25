from contextlib import suppress
from rest_framework.permissions import BasePermission
from .models import Board
from .decorators import false_on_exception
import argon2, base64


class BoardPermission(BasePermission):
    message = 'Credentials not provied'

    @false_on_exception
    def has_permission(self, request, view):
        if not (auth := request.headers.get('Authentication', '')): return False

        auth = base64.b64decode(auth.encode('ascii')).decode('ascii')
        id, password = auth.split(' ')

        try: board = Board.objects.get(pk=id)
        except Board.DoesNotExist: return False

        ph = argon2.PasswordHasher()
        try:
            ph.verify(board.password, password)
            if ph.check_needs_rehash(board.password):
                board.password = ph.hash(password)
                board.save()
            request.board = board
            return True
        except argon2.exceptions.VerifyMismatchError: return False

    @false_on_exception
    def has_object_permission(self, request, view, obj):
        return request.board.pk == obj.pk
