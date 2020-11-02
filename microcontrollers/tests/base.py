from abc import ABC
import pytest
from django.urls import reverse
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

        board.delete()

    @pytest.fixture
    def pin_data(self, board):
        def generate_data(digital=True, **override):
            data = {
                'board': board[0].pk,
                'number': 1,
                'value': 'ON' if digital else '255',
                'is_digital': digital,
                'description': 'Test Pin',
            }
            data.update(override)
            return data
        
        return generate_data

    @pytest.fixture
    def pin(self, db, pin_data):
        data = pin_data()
        data['board'] = Board.objects.get(pk=data['board'])
        pin = Pin.objects.create(**data)

        yield pin, data

        pin.delete()
