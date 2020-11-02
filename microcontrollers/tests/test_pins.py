import pytest
from django.urls import reverse
from .base import BaseMicrocontrollerTest


class TestPins(BaseMicrocontrollerTest):
    list_url = lambda: reverse('pin-list')
    detail_url = lambda pk: reverse('pin-detail', kwargs={'pk': pk})

    def test_unauthenticated_access(self, client, pin, pin_data):
        list_url = TestPins.list_url()
        detail_url = TestPins.detail_url(pk=pin[0].pk)

        resp = client.get(list_url)
        assert resp.status_code == 403

        resp = client.post(list_url, data=pin_data())
        assert resp.status_code == 403

        resp = client.get(detail_url)
        assert resp.status_code == 403

        resp = client.put(
            detail_url,
            pin_data(value='OFF'),
            content_type='application/json',
        )
        assert resp.status_code == 403

        resp = client.patch(
            detail_url,
            pin_data(value='OFF'),
            content_type='application/json',
        )
        assert resp.status_code == 403

        resp = client.delete(detail_url)
        assert resp.status_code == 403

    def test_authenticated_access(self, admin_client, pin_data):
        list_url = TestPins.list_url()

        resp = admin_client.get(list_url)
        assert resp.status_code == 200

        data = pin_data()

        resp = admin_client.post(list_url, data)
        assert resp.status_code == 201

        detail_url = TestPins.detail_url(pk=resp.json()['id'])

        resp = admin_client.get(detail_url)
        assert resp.status_code == 200

        resp = admin_client.put(
            detail_url,
            {**data, 'value': 'OFF'},
            content_type='application/json',
        )
        assert resp.status_code == 200

        resp = admin_client.patch(
            detail_url,
            {'is_digital': False, 'value': '255'},
            content_type='application/json',
        )
        assert resp.status_code == 200

        resp = admin_client.delete(detail_url)
        assert resp.status_code == 204
