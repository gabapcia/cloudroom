import argon2, jwt, os, datetime
from rest_framework import status, response
from django.core.exceptions import ObjectDoesNotExist
from board import models, serializers


def validate_board(body:dict) -> response.Response:
    if 'id' not in body and \
        'password' not in body:
        return response.Response(
            data={'detail': 'Auth data not provied'},
            status=status.HTTP_400_BAD_REQUEST
        )
    ph = argon2.PasswordHasher()
    try:
        board = models.Board.objects.get(pk=body['id'])
        ph.verify(board.password, body['password'])
    except ObjectDoesNotExist:
        return response.Response(
            data={'detail': 'Board does not exist'},
            status=status.HTTP_400_BAD_REQUEST
        )
    except argon2.exceptions.VerifyMismatchError:
        return response.Response(
            data={'detail': 'Invalid password'},
            status=status.HTTP_401_UNAUTHORIZED
        )

    if ph.check_needs_rehash(board.password):
        board.password = ph.hash(board['password'])
        board.save()
    
    if not board.allowed:
        return response.Response(
            data={'detail': 'This board is actually suspended'},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    token = jwt.encode(
        payload={
            'id': board.id,
            'exp': datetime.datetime.now() + datetime.timedelta(days=1),
        },
        key=os.getenv('JWT_SECRET'),
    ).decode()

    return response.Response(
        data={'token': token},
        status=status.HTTP_201_CREATED,
    )


def board_pin_list(token:str) -> response.Response:
    try:
        board_id = jwt.decode(
            jwt=token, 
            key=os.getenv('JWT_SECRET'),
        )['id']
    except jwt.ExpiredSignatureError:
        return response.Response(
            data={'detail': 'Token has expired'},
            status=status.HTTP_401_UNAUTHORIZED,
        )
    
    board = models.Board.objects.get(pk=board_id)
    board.last_request = datetime.datetime.now()
    board.save()

    pins = serializers.PinSerializer(
        board.pin_set,
        many=True
    )

    return response.Response(data=pins.data, status=status.HTTP_200_OK)
