import requests
from typing import Dict, List

from .utils.exceptions import RequestError


def search(text:List[str]) -> Dict[str, str]:
    response = requests.get(
        url='https://api.duckduckgo.com/',
        params={'q': ' '.join(text), 'format': 'json'}
    )

    if response.status_code >= 300 or response.status_code < 200:
        raise RequestError(
            http_status=response.status_code,
            description=response.text
        )

    response = response.json()

    return {
        'text': response['AbstractText'],
        'url': response['AbstractURL'],
        'source': response['AbstractSource']
    }


if __name__ == "__main__":
    search(text=['glados'])
