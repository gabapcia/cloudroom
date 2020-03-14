import argon2, os, datetime, base64, re
from rest_framework import status, response
from django.core.exceptions import ObjectDoesNotExist
from board import models, serializers
from board.util import exceptions


def validate_board(header:str) -> models.Board:
    auth = base64.b64decode(header.encode()).decode()
    board_id, password = auth.split(':') 
    
    ph = argon2.PasswordHasher()
    try:
        board = models.Board.objects.get(pk=board_id)
        ph.verify(board.password, password)
    except ObjectDoesNotExist:
        raise exceptions.BoardAuthError(
            data={'detail': 'Board does not exist'},
            status=status.HTTP_400_BAD_REQUEST
        )
    except argon2.exceptions.VerifyMismatchError:
        raise exceptions.BoardAuthError(
            data={'detail': 'Invalid password'},
            status=status.HTTP_401_UNAUTHORIZED
        )

    if ph.check_needs_rehash(board.password):
        board.password = ph.hash(board['password'])
        board.save()
    
    if not board.allowed:
        raise exceptions.BoardAuthError(
            data={'detail': 'This board is actually suspended'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    return board


def board_pin_list(request) -> response.Response:
    if 'Board-Token' not in request.headers:
        return response.Response(
            data={'detail': 'Authentication credentials were not provided'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    if not re.search(r'^Basic ', request.headers['Board-Token']):
        return response.Response(
            data={'detail': 'Token malformatted'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    token = request.headers['Board-Token'].split(' ')[1]
    try:
        board = validate_board(
            header=token
        )
    except exceptions.BoardAuthError as e:
        return response.Response(
            data=e.data,
            status=e.status,
        )
    
    board.last_request = datetime.datetime.now()
    board.save()

    pins = serializers.PinSerializer(
        board.pin_set,
        many=True,
        fields=(
            'number',
            'status',
            'mode',
            'configuration'
        )
    )

    return response.Response(
        data=pins.data, 
        status=status.HTTP_200_OK
    )
