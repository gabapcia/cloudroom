from django.urls import reverse
from ..models import Board
from .base import BaseMicrocontrollerTest


class TestBoards(BaseMicrocontrollerTest):
    def _list_url() -> str:
        return reverse('board-list')

    def _detail_url(pk: int) -> str:
        return reverse('board-detail', kwargs={'pk': pk})

    def _update_secret_url(pk: int) -> str:
        return reverse('board-generate-new-secret', kwargs={'pk': pk})

    def _validate_secret_url(pk: int) -> str:
        return reverse('board-validate-secret', kwargs={'pk': pk})

    def _pins_url(pk: int) -> str:
        return reverse('board-pins', kwargs={'pk': pk})

    def test_unauthenticated_access(self, client, board, board_data):
        list_url = TestBoards._list_url()
        detail_url = TestBoards._detail_url(pk=board[0].pk)
        pins_url = TestBoards._pins_url(pk=board[0].pk)

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

        resp = client.get(pins_url)
        assert resp.status_code == 403

    def test_authenticated_access(self, admin_client, board_data):
        list_url = TestBoards._list_url()

        resp = admin_client.get(list_url)
        assert resp.status_code == 200

        data = board_data()

        resp = admin_client.post(list_url, data)
        assert resp.status_code == 201

        pk = resp.json()['id']
        detail_url = TestBoards._detail_url(pk=pk)

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

        pins_url = TestBoards._pins_url(pk=pk)
        resp = admin_client.get(pins_url)
        assert resp.status_code == 200

        resp = admin_client.delete(detail_url)
        assert resp.status_code == 204

    def test_invalid_status(self, admin_client, board, board_data):
        list_url = TestBoards._list_url()
        detail_url = TestBoards._detail_url(pk=board[0].pk)
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

    def test_board_with_repeated_name(self, admin_client, board):
        data = board[1]
        list_url = TestBoards._list_url()

        resp = admin_client.post(
            list_url,
            data,
            content_type='application/json',
        )
        assert resp.status_code == 400

    def test_change_board_name(self, admin_client, board):
        pk = board[0].pk

        detail_url = TestBoards._detail_url(pk=pk)
        data = admin_client.get(
            detail_url,
            content_type='application/json'
        ).json()
        data.update(board[1])

        resp = admin_client.put(
            detail_url,
            {**data, 'name': 'random name'},
            content_type='application/json',
        )
        assert resp.status_code == 200
        assert resp.json()['name'] == data['name']

        resp = admin_client.patch(
            detail_url,
            {'name': 'random name'},
            content_type='application/json',
        )
        assert resp.status_code == 200
        assert resp.json()['name'] == data['name']

    def test_update_board_secret(self, admin_client, board):
        pk = board[0].pk
        secret = board[1]['secret']

        update_secret_url = TestBoards._update_secret_url(pk=pk)
        resp = admin_client.patch(update_secret_url)
        assert resp.status_code == 200
        new_secret = resp.json().get('secret')
        assert new_secret is not None
        assert new_secret != secret

    def test_validate_board_secret(self, admin_client, board):
        pk = board[0].pk
        secret = board[1]['secret']

        validate_secret_url = TestBoards._validate_secret_url(pk=pk)
        resp = admin_client.post(
            validate_secret_url,
            {'secret': secret},
            content_type='application/json',
        )
        assert resp.status_code == 204

    def test_validate_old_secret(self, admin_client, board):
        pk = board[0].pk
        old_secret = board[1]['secret']

        update_secret_url = TestBoards._update_secret_url(pk=pk)
        admin_client.patch(update_secret_url)

        validate_secret_url = TestBoards._validate_secret_url(pk=pk)
        resp = admin_client.post(
            validate_secret_url,
            {'secret': old_secret},
            content_type='application/json',
        )
        assert resp.status_code == 400
