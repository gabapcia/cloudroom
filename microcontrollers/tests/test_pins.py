from django.urls import reverse
from .base import BaseMicrocontrollerTest


class TestPins(BaseMicrocontrollerTest):
    def _list_url() -> str:
        return reverse('pin-list')

    def _detail_url(pk: int) -> str:
        return reverse('pin-detail', kwargs={'pk': pk})

    def test_unauthenticated_access(self, client, pin, pin_data):
        list_url = TestPins._list_url()
        detail_url = TestPins._detail_url(pk=pin[0].pk)

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
        list_url = TestPins._list_url()

        resp = admin_client.get(list_url)
        assert resp.status_code == 200

        data = pin_data()

        resp = admin_client.post(list_url, data)
        assert resp.status_code == 201

        detail_url = TestPins._detail_url(pk=resp.json()['id'])

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
        print(resp.json())
        assert resp.status_code == 200

        resp = admin_client.delete(detail_url)
        assert resp.status_code == 204

    def test_save_pin_twice_same_board(self, admin_client, pin_data):
        data = pin_data()

        list_url = TestPins._list_url()
        for _ in range(2):
            resp = admin_client.post(
                list_url,
                data,
                content_type='application/json',
            )
        assert resp.status_code == 400

    def test_save_pin_with_negative_number(self, pin_data, admin_client):
        data = pin_data(number=-1)
        list_url = TestPins._list_url()

        resp = admin_client.post(
            list_url,
            data,
            content_type='application/json',
        )
        assert resp.status_code == 400

    def test_invalid_value_for_digital_pin(self, pin_data, admin_client):
        list_url = TestPins._list_url()

        resp = admin_client.post(
            list_url,
            pin_data(is_digital=True, value='123'),
            content_type='application/json',
        )
        assert resp.status_code == 400

    def test_invalid_value_for_a_non_digital_pin(self, pin_data, admin_client):
        list_url = TestPins._list_url()

        resp = admin_client.post(
            list_url,
            pin_data(is_digital=False, value='ON'),
            content_type='application/json',
        )
        assert resp.status_code == 400

    def test_pin_with_invalid_board(self, admin_client, pin_data):
        list_url = TestPins._list_url()
        data = pin_data(board='invalid board')

        resp = admin_client.post(
            list_url,
            data,
            content_type='application/json',
        )
        assert resp.status_code == 400

    def test_pin_without_board(self, admin_client, pin_data):
        list_url = TestPins._list_url()
        data = pin_data(board=None)

        resp = admin_client.post(
            list_url,
            data,
            content_type='application/json',
        )
        assert resp.status_code == 400

    def test_change_pin_number(self, admin_client, pin):
        pk = pin[0].pk
        number = pin[0].number

        detail_url = TestPins._detail_url(pk=pk)
        data = admin_client.get(
            detail_url,
            content_type='application/json'
        ).json()
        data.update(pin[1])

        resp = admin_client.put(
            detail_url,
            {**data, 'number': number + 1},
            content_type='application/json',
        )
        assert resp.status_code == 200
        assert resp.json()['number'] == data['number']

        resp = admin_client.patch(
            detail_url,
            {'number': number + 1},
            content_type='application/json',
        )
        assert resp.status_code == 200
        assert resp.json()['number'] == data['number']

    def test_change_pin_board(self, admin_client, pin):
        pk = pin[0].pk
        board = pin[0].board.pk

        detail_url = TestPins._detail_url(pk=pk)
        data = admin_client.get(
            detail_url,
            content_type='application/json'
        ).json()
        data.update(pin[1])

        resp = admin_client.put(
            detail_url,
            {**data, 'board': board + 1},
            content_type='application/json',
        )
        assert resp.status_code == 200
        assert resp.json()['board'] == data['board']

        resp = admin_client.patch(
            detail_url,
            {'board': board + 1},
            content_type='application/json',
        )
        assert resp.status_code == 200
        assert resp.json()['board'] == data['board']

    def test_change_pin_value_without_type(self, admin_client, pin):
        pk = pin[0].pk
        if pin[0].is_digital:
            value = 'OFF' if pin[0].value == 'ON' else 'ON'
        else:
            value = ''.join(reversed(pin[0].value))

        detail_url = TestPins._detail_url(pk=pk)
        data = admin_client.get(
            detail_url,
            content_type='application/json'
        ).json()
        data.update(pin[1])

        resp = admin_client.put(
            detail_url,
            {'value': value},
            content_type='application/json',
        )
        assert resp.status_code == 400

        resp = admin_client.patch(
            detail_url,
            {'value': value},
            content_type='application/json',
        )
        assert resp.status_code == 400

    def test_change_pin_type_without_value(self, admin_client, pin):
        detail_url = TestPins._detail_url(pk=pin[0].pk)
        data = admin_client.get(
            detail_url,
            content_type='application/json'
        ).json()
        data.update(pin[1])

        resp = admin_client.put(
            detail_url,
            {**data, 'is_digital': not data['is_digital']},
            content_type='application/json',
        )
        assert resp.status_code == 400

        resp = admin_client.patch(
            detail_url,
            {'is_digital': not data['is_digital']},
            content_type='application/json',
        )
        assert resp.status_code == 400

    def test_create_pin_with_value_gt_1023(self, admin_client, pin_data):
        list_url = TestPins._list_url()

        resp = admin_client.post(
            list_url,
            pin_data(is_digital=False, value=1024),
            content_type='application/json',
        )
        assert resp.status_code == 400

    def test_update_pin_with_value_gt_1023(self, admin_client, pin):
        detail_url = TestPins._detail_url(pk=pin[0].pk)

        resp = admin_client.put(
            detail_url,
            {**pin[1], 'is_digital': False, 'value': 1024},
            content_type='application/json',
        )
        assert resp.status_code == 400

        resp = admin_client.patch(
            detail_url,
            {'is_digital': False, 'value': 1024},
            content_type='application/json',
        )
        assert resp.status_code == 400
