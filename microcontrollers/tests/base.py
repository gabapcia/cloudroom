from abc import ABC
from contextlib import suppress
import pytest
from django.urls import reverse
from django.db.transaction import TransactionManagementError
from cloudroom.testing import BaseTest
from ..models import Board, Pin


class BaseMicrocontrollerTest(BaseTest, ABC):
    @pytest.fixture
    def board_data(self, faker):
        def generate_data(**overwrite):
            data = {
                'name': f'Test #{faker.unique.random_int(max=10000)}',
                'status': Board.Status.ACTIVATED,
            }
            data.update(overwrite)
            return data

        return generate_data

    @pytest.fixture
    def board(self, db, board_data):
        data = board_data()
        board = Board.objects.create(**data)

        yield board, data

        with suppress(TransactionManagementError):
            board.delete()

    @pytest.fixture
    def pin_data(self, faker, board):
        def generate_data(is_digital=True, **override):
            value = 'ON' if is_digital else str(faker.random_int(max=1024))

            data = {
                'board': board[0].pk,
                'number': faker.unique.random_int(max=55),
                'value': value,
                'is_digital': is_digital,
                'description': 'Test Pin',
            }
            data.update(override)
            return data
        
        return generate_data

    @pytest.fixture
    def pin(self, db, pin_data):
        data = pin_data()
        pin = Pin.objects.create(**{
            **data,
            'board': Board.objects.get(pk=data['board']),
        })

        yield pin, data

        with suppress(TransactionManagementError):
            pin.delete()
