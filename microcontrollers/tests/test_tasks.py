import json
import pytest
import paho.mqtt.subscribe as subscribe
from cloudroom.mqtt import Manager as MQTTManager
from .base import BaseMicrocontrollerTest
from ..utils import build_topic
from ..tasks import notify_board, change_pin_value
from ..serializers.pin import BasicPinInfoSerializer


class TestTasks(BaseMicrocontrollerTest):
    def test_change_pin_value(self, pin):
        pin = pin[0]
        value = 'OFF' if pin.value == 'ON' else 'ON'
        change_pin_value(pin_id=pin.pk, value=value)

        pin.refresh_from_db()

        assert pin.value == value

    @pytest.mark.timeout(10)
    def test_notify_board(self, pin):
        manager = MQTTManager()

        pin = pin[0]
        topic = build_topic(board_id=pin.board.pk)
        payload = BasicPinInfoSerializer(pin).data
        notify_board(topic=topic, pin_id=pin.pk)

        msg = subscribe.simple(
            topics=topic,
            msg_count=1,
            qos=1,
            hostname=manager._hostname,
            port=manager._port,
            auth={
                'username': manager._username,
                'password': manager._password,
            },
        )

        assert msg.topic == topic
        assert json.loads(msg.payload) == payload
