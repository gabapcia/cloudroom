import json
from copy import deepcopy
import pytest
import paho.mqtt.subscribe as subscribe
from ..mqtt import Manager as MQTTManager
from ..mqtt.exceptions import (
    BrokerRequestError,
    InvalidPassword,
    InvalidUsername,
)


class TestMQTTManager:
    manager = MQTTManager()

    @pytest.fixture
    def manager_modified(self):
        manager = deepcopy(self.manager)
        manager._url += '/invalid-path'
        return manager

    @pytest.mark.order(1)
    def test_user_creation(self):
        self.manager.create_user(username='test', password='test')

    @pytest.mark.order(2)
    def test_grant_user_permissions(self):
        self.manager.grant_user_permissions(username='test')

    @pytest.mark.order(3)
    def test_user_password_update(self):
        self.manager.update_user_password(
            username='test',
            new_password='new',
        )

    @pytest.mark.order(4)
    def test_user_deletion(self):
        self.manager.delete_user(username='test')

    def test_create_user_without_username(self):
        with pytest.raises(InvalidUsername):
            self.manager.create_user(username=None, password='test')

    def test_create_user_without_password(self):
        with pytest.raises(InvalidPassword):
            self.manager.create_user(username='test', password=None)

    def test_grant_unknown_user_permission(self):
        with pytest.raises(BrokerRequestError):
            self.manager.grant_user_permissions(username='test')

    def test_grant_empty_username_user_permission(self):
        with pytest.raises(InvalidUsername):
            self.manager.grant_user_permissions(username=None)

    def test_delete_user_with_empty_username(self):
        with pytest.raises(InvalidUsername):
            self.manager.delete_user(username=None)

    def test_delete_invalid_user(self):
        self.manager.delete_user(username='unknown')

    def test_create_user_with_unavailable_broker(self, manager_modified):
        with pytest.raises(BrokerRequestError):
            manager_modified.create_user(username='test', password='test')

    def test_update_user_with_unavailable_broker(self, manager_modified):
        with pytest.raises(BrokerRequestError):
            manager_modified.update_user_password(
                username='test',
                new_password='test',
            )

    def test_delete_user_with_unavailable_broker(self, manager_modified):
        with pytest.raises(BrokerRequestError):
            manager_modified.delete_user(username='test')

    @pytest.mark.timeout(10)
    def test_send_message(self):
        topic = 'test'
        payload = {'foo': 'bar'}

        self.manager.publish(topic=topic, payload=payload, qos=1)

        msg = subscribe.simple(
            topics=topic,
            msg_count=1,
            qos=1,
            hostname=self.manager._hostname,
            port=self.manager._port,
            auth={
                'username': self.manager._username,
                'password': self.manager._password,
            },
        )

        assert msg.topic == topic
        assert json.loads(msg.payload) == payload
