import pytest
from django.urls import reverse
from ..models import Board
from .base import BaseMicrocontrollerTest


class TestBoards(BaseMicrocontrollerTest):
    list_url = lambda: reverse('board-list')
    detail_url = lambda pk: reverse('board-detail', kwargs={'pk': pk})

    def test_unauthenticated_access(self, client, board, board_data):
        list_url = TestBoards.list_url()
        detail_url = TestBoards.detail_url(pk=board[0].pk)

        resp = client.get(list_url)
        assert resp.status_code == 403

        resp = client.post(list_url, data=board_data())
        assert resp.status_code == 403

        resp = client.get(detail_url)
        assert resp.status_code == 403

        resp = client.put(
            detail_url,
            board_data(status=Board.Status.DEACTIVATED),
            content_type='application/json',
        )
        assert resp.status_code == 403

        resp = client.patch(
            detail_url,
            board_data(status=Board.Status.DEACTIVATED),
            content_type='application/json',
        )
        assert resp.status_code == 403

        resp = client.delete(detail_url)
        assert resp.status_code == 403

    def test_authenticated_access(self, admin_client, board_data):
        list_url = TestBoards.list_url()

        resp = admin_client.get(list_url)
        assert resp.status_code == 200

        data = board_data()

        resp = admin_client.post(list_url, data)
        assert resp.status_code == 201

        detail_url = TestBoards.detail_url(pk=resp.json()['id'])

        resp = admin_client.get(detail_url)
        assert resp.status_code == 200

        resp = admin_client.put(
            detail_url,
            {**data, 'status': Board.Status.DEACTIVATED.value},
            content_type='application/json',
        )
        assert resp.status_code == 200

        resp = admin_client.patch(
            detail_url,
            {'status': Board.Status.BLOCKED.value},
            content_type='application/json',
        )
        assert resp.status_code == 200

        resp = admin_client.delete(detail_url)
        assert resp.status_code == 204

    def test_invalid_status(self, admin_client, board, board_data):
        list_url = TestBoards.list_url()
        detail_url = TestBoards.detail_url(pk=board[0].pk)
        data = board_data(status='invalid status')

        resp = admin_client.post(list_url, data)
        assert resp.status_code == 400

        resp = admin_client.put(
            detail_url,
            {**board[1], 'status': 'invalid status'},
            content_type='application/json',
        )
        assert resp.status_code == 400

        resp = admin_client.patch(
            detail_url,
            {'status': 'invalid status'},
            content_type='application/json',
        )
        assert resp.status_code == 400
