from dataclasses import dataclass


@dataclass
class RequestError(Exception):
    http_status: int

    def __str__(self):
        return f'The server returned a {self.http_status} code'


@dataclass
class NoResposeFound(Exception):
    keyword: str

    def __str__(self):
        return f'Nothing found for "{self.keyword}"'
