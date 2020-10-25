from abc import ABC
import pytest
from cloudroom.utils.test import BaseTests
from ..models import Board, Pin
from ..serializers import BoardSerializer, PinSerializer


class BaseBoardTests(BaseTests, ABC):
    BOARD_STATUS = Board.Status

    @pytest.fixture
    def board(self, db):
        data = dict(
            password=self._generate_random_string(),
            name=self._generate_random_string(),
            status=Board.Status.ACTIVATED,
        )
        board = Board.objects.create(**data)
        return BoardSerializer(board).data, data

    @pytest.fixture
    def pin(self, board, db):
        data = dict(
            number=1,
            value='ON',
            is_digital=True,
            description='Test Pin',
            board=Board.objects.get(pk=board[0]['id'])
        )
        pin = Pin.objects.create(**data)
        return PinSerializer(pin).data, data
