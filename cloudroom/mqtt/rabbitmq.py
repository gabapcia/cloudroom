import json
from contextlib import suppress
from json.decoder import JSONDecodeError
from typing import Any
import requests
from django.conf import settings
from requests.models import HTTPBasicAuth
import paho.mqtt.publish as paho
from .exceptions import (
    BrokerRequestError,
    BrokerPublishError,
    InvalidPassword,
    InvalidUsername,
)


class Manager:
    def __init__(self) -> None:
        self._url = f'{settings.MQTT_BROKER_MANAGEMENT_URL}/api'
        self._hostname = settings.MQTT_BROKER_HOST
        self._port = int(settings.MQTT_BROKER_PORT)
        self._username = settings.MQTT_BROKER_USERNAME
        self._password = settings.MQTT_BROKER_PASSWORD
        self._authorization = HTTPBasicAuth(self._username, self._password)

    def create_user(self, username: str, password: str) -> None:
        if not username:
            raise InvalidUsername

        if not password:
            raise InvalidPassword

        r = requests.put(
            f'{self._url}/users/{username}',
            json={'password': password, 'tags': ''},
            auth=self._authorization,
        )
        if not r.ok:
            body = {}
            with suppress(JSONDecodeError):
                body = r.json()

            raise BrokerRequestError(r.status_code, body)

    def grant_user_permissions(self, username: str) -> None:
        if not username:
            raise InvalidUsername

        r = requests.put(
            f'{self._url}/permissions/%2F/{username}',
            json={'configure': '.*', 'write': '.*', 'read': '.*'},
            auth=self._authorization,
        )
        if not r.ok:
            body = {}
            with suppress(JSONDecodeError):
                body = r.json()

            raise BrokerRequestError(r.status_code, body)

    def update_user_password(self, username: str, new_password: str) -> None:
        self.create_user(username, new_password)

    def delete_user(self, username: str) -> None:
        if not username:
            raise InvalidUsername

        r = requests.delete(
            f'{self._url}/users/{username}',
            auth=self._authorization,
        )
        if not r.ok:
            if r.status_code == 404:
                return

            body = {}
            with suppress(JSONDecodeError):
                body = r.json()

            raise BrokerRequestError(r.status_code, body)

    def publish(
        self,
        topic: str,
        payload: dict[str, Any],
        qos: int = 1,
    ) -> None:
        try:
            paho.single(
                topic=topic,
                payload=json.dumps(payload),
                qos=qos,
                retain=True,
                hostname=self._hostname,
                port=self._port,
                auth={'username': self._username, 'password': self._password},
            )
        except Exception as e:  # pragma: no cover
            raise BrokerPublishError from e
