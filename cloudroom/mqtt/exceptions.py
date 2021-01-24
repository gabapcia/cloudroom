from typing import Any


class BrokerRequestError(Exception):
    def __init__(self, code: str, body: dict[str, Any]) -> None:
        self.code = code
        self.body = body

    def __str__(self) -> str:  # pragma: no cover
        return f'Broker returned a status code: {self.code}'


class BrokerPublishError(Exception):
    pass


class InvalidUsername(Exception):
    pass


class InvalidPassword(Exception):
    pass
