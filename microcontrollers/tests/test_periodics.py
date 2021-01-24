from django.urls.base import reverse
from .base import BaseMicrocontrollerTest
from ..models import PeriodicPinBehavior


class TestPeriodicBehavior(BaseMicrocontrollerTest):
    def list_url(self) -> str:
        return reverse('periodicpinbehavior-list')

    def detail_url(self, pk: int) -> str:
        return reverse('periodicpinbehavior-detail', kwargs={'pk': pk})

    def test_unauthenticated_access(self, client):
        list_url = self.list_url()
        detail_url = self.detail_url(pk=1)
        resp = client.get(list_url)
        assert resp.status_code == 403

        resp = client.post(list_url, {})
        assert resp.status_code == 403

        resp = client.delete(detail_url)
        assert resp.status_code == 403

    def test_create_periodic_pin_task(self, admin_client, periodic_pin_data):
        data = periodic_pin_data()
        url = self.list_url()
        resp = admin_client.post(url, data, content_type='application/json')
        assert resp.status_code == 201
        pk = resp.json()['id']
        assert PeriodicPinBehavior.objects.filter(pk=pk).exists()

    def test_create_periodic_pin_task_without_pin(
        self,
        admin_client,
        periodic_pin_data,
    ):
        data = periodic_pin_data()
        data.pop('pin')

        url = self.list_url()
        resp = admin_client.post(url, data, content_type='application/json')
        assert resp.status_code == 400

    def test_create_periodic_pin_task_without_task(
        self,
        admin_client,
        periodic_pin_data,
    ):
        data = periodic_pin_data()
        data['task'].pop('task')

        url = self.list_url()
        resp = admin_client.post(url, data, content_type='application/json')
        assert resp.status_code == 400

    def test_create_periodic_pin_task_without_kwargs(
        self,
        admin_client,
        periodic_pin_data,
    ):
        data = periodic_pin_data()
        data['task'].pop('kwargs')

        url = self.list_url()
        resp = admin_client.post(url, data, content_type='application/json')
        assert resp.status_code == 400

    def test_delete_periodic_pin_task(
        self,
        admin_client,
        periodic_pin,
    ):
        pk = periodic_pin[0].pk

        url = self.detail_url(pk=pk)
        resp = admin_client.delete(url, content_type='application/json')
        assert resp.status_code == 204
        assert not PeriodicPinBehavior.objects.filter(pk=pk).exists()

    def test_retrieve_periodic_pin_task(
        self,
        admin_client,
        periodic_pin,
    ):
        pk = periodic_pin[0].pk

        url = self.detail_url(pk=pk)
        resp = admin_client.get(url)
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, dict)
        assert data['id'] == pk
