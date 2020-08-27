import pytest
from django.urls import reverse
from django.urls.exceptions import NoReverseMatch
from ..models import Correios
from ..serializers import CorreiosSerializer


URLS = [
    lambda kwargs: reverse('correios-list', kwargs=kwargs),
    lambda kwargs: reverse('correios-detail', kwargs=kwargs),
]


class TestCorreios:
    @pytest.fixture
    def order(self, db):
        order, _ = Correios.objects.get_or_create(
            code='AA000000000AA',
            name='Test Order'
        )
        return CorreiosSerializer(order).data

    @pytest.mark.parametrize('url', URLS)
    def test_anonymous_access(self, client, url, order):
        try:
            response = client.get(url(kwargs={}))
        except NoReverseMatch:
            response = client.get(url(kwargs={'pk': order['id']}))
    
        assert response.status_code == 403

    @pytest.mark.parametrize('url', URLS)
    def test_admin_access(self, admin_client, url, order):
        try:
            response = admin_client.get(url(kwargs={}))
        except NoReverseMatch:
            response = admin_client.get(url(kwargs={'pk': order['id']}))

        assert response.status_code == 200
