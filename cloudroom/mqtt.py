from typing import Any
import requests
from django.conf import settings
from requests.models import HTTPBasicAuth
import paho.mqtt.publish as paho


class Manager:
    def __init__(self) -> None:
        self._url = f'{settings.MQTT_BROKER_MANAGEMENT_URL}/api'
        self._hostname = settings.MQTT_BROKER_HOST
        self._port = settings.MQTT_BROKER_PORT
        self._username = settings.MQTT_BROKER_USERNAME
        self._password = settings.MQTT_BROKER_PASSWORD
        self._authorization = HTTPBasicAuth(self._username, self._password)

    def create_user(self, username: str, password: str) -> None:
        r = requests.put(
            f'{self._url}/users/{username}',
            json={'password': password, 'tags': ''},
            auth=self._authorization,
        )
        if not r.ok:
            raise Exception('Error creating user')

    def grant_user_permissions(self, username: str) -> None:
        r = requests.put(
            f'{self._url}/permissions/%2F/{username}',
            json={'configure': '', 'write': '.*','read': '.*'},
            auth=self._authorization,
        )
        if not r.ok:
            raise Exception('Error granting user permissions')

    def update_user_password(self, username: str, new_password: str) -> None:
        self.create_user(username, new_password)

    def delete_user(self, username: str) -> None:
        r = requests.delete(
            f'{self._url}/users/{username}',
            auth=self._authorization,
        )
        if not r.ok:
            raise Exception('Error deleting user')

    def publish(self, topic: str, payload: dict[str, Any]) -> None:
        paho.single(
            topic=topic,
            payload=payload,
            qos=1,
            hostname=self._hostname,
            port=self._port,
            auth={'username': self._username, 'password': self._password},
        )
