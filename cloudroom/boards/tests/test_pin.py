import pytest
from django.urls import reverse
from django.urls.exceptions import NoReverseMatch
from .test_setup import BaseBoardTests


URLS = [
    lambda kwargs: reverse('pin-list', kwargs=kwargs),
    lambda kwargs: reverse('pin-detail', kwargs=kwargs),
]


class TestsPin(BaseBoardTests):
    @pytest.mark.parametrize('url', URLS)
    def test_anonymous_access(self, client, url, pin):
        try:
            response = client.get(url(kwargs={}))
        except NoReverseMatch:
            response = client.get(url(kwargs={'pk': pin[0]['id']}))

        assert response.status_code == 403

    @pytest.mark.parametrize('url', URLS)
    def test_admin_access(self, admin_client, url, pin):
        try:
            response = admin_client.get(url(kwargs={}))
        except NoReverseMatch:
            response = admin_client.get(url(kwargs={'pk': pin[0]['id']}))

        assert response.status_code == 200

    def test_create_pin(self, admin_client, board, pin):
        pin_data = {
            'number': pin[0]['number'] + 1,
            'value': 'ON',
            'is_digital': True,
            'description': "Test Pin",
            'board': board[0]['id']
        }
        response = admin_client.post(reverse('pin-list'), pin_data)
        assert response.status_code == 201

    def test_update_pin(self, admin_client, client, pin):
        url = reverse('pin-detail', kwargs={'pk': pin[0]['id']})

        updated_data = {**pin[0], 'value': 'OFF'}
        response = client.put(
            url,
            updated_data,
            content_type='application/json'
        )
        assert response.status_code == 403

        response = client.patch(
            url,
            {'value': 'OFF'},
            content_type='application/json'
        )
        assert response.status_code == 403

        response = admin_client.put(
            url,
            updated_data,
            content_type='application/json'
        )
        assert response.status_code == 200
        assert response.json()['value'] == 'OFF'

        response = admin_client.patch(
            url,
            {'value': 'ON'},
            content_type='application/json'
        )
        assert response.status_code == 200
        assert response.json()['value'] == 'ON'

    def test_pin_integrity_check(self, admin_client, pin):
        url = reverse('pin-detail', kwargs={'pk': pin[0]['id']})

        response = admin_client.patch(
            url,
            {'value': '123'},
            content_type='application/json'
        )
        assert response.status_code == 400

    def test_delete_pin(self, admin_client, client, pin):
        url = reverse('pin-detail', kwargs={'pk': pin[0]['id']})

        response = client.delete(url)
        assert response.status_code == 403

        response = admin_client.delete(url)
        assert response.status_code == 204
