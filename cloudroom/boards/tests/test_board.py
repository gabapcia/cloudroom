import base64
import pytest
from django.urls import reverse
from django.urls.exceptions import NoReverseMatch
from .test_setup import BaseBoardTests
from ..models import Board


URLS = [
    lambda kwargs: reverse('board-list', kwargs=kwargs),
    lambda kwargs: reverse('board-detail', kwargs=kwargs),
    lambda kwargs: reverse('board-pins', kwargs=kwargs),
]


class TestsBoard(BaseBoardTests):
    @pytest.mark.parametrize('url', URLS)
    def test_anonymous_access(self, client, url, board):
        try:
            response = client.get(url(kwargs={}))
        except NoReverseMatch:
            response = client.get(url(kwargs={'pk': board[0]['id']}))
    
        assert response.status_code == 403
    
    @pytest.mark.parametrize('url', URLS)
    def test_admin_access(self, admin_client, url, board):
        try:
            response = admin_client.get(url(kwargs={}))
        except NoReverseMatch:
            response = admin_client.get(url(kwargs={'pk': board[0]['id']}))

        assert response.status_code == 200

    def test_create_board(self, admin_client, client):
        board_data = {
            'password': self._generate_random_string(),
            'name': self._generate_random_string(),
            'status': Board.Status.ACTIVATED,
        }
        response = client.post(reverse('board-list'), board_data)
        assert response.status_code == 403

        response = admin_client.post(reverse('board-list'), board_data)
        assert response.status_code == 201

    def test_get_board_pins(self, admin_client, client, board):
        url = reverse('board-pins', kwargs={'pk': board[0]['id']})

        response = admin_client.get(url)
        assert response.status_code == 200

        response = client.get(url)
        assert response.status_code == 403

        board_auth = base64.b64encode(
            f"{board[0]['id']} {board[1]['password']}".encode()
        ).decode()
        response = client.get(url, HTTP_AUTHORIZATION=board_auth)
        assert response.status_code == 200

    def test_update_board(self, admin_client, client, board):
        url = reverse('board-detail', kwargs={'pk': board[0]['id']})

        data = {**board[0], **board[1]}
        put_data = {**data, 'status': Board.Status.DEACTIVATED}
        response = client.put(url, put_data)
        assert response.status_code == 403

        response = client.patch(url, {'status': Board.Status.DEACTIVATED})
        assert response.status_code == 403

        response = admin_client.put(
            url,
            put_data,
            content_type='application/json'
        )
        assert response.status_code == 200

        response = admin_client.patch(
            url,
            {'status': Board.Status.DEACTIVATED},
            content_type='application/json'
        )
        assert response.status_code == 200

    def test_delete_board(self, admin_client, client, board):
        url = reverse('board-detail', kwargs={'pk': board[0]['id']})

        response = client.delete(url)
        assert response.status_code == 403

        response = admin_client.delete(url)
        assert response.status_code == 204
