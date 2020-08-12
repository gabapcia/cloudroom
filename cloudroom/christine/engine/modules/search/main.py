import requests
from typing import Dict, List

from .exceptions import RequestError, NoResposeFound


def process(params:List[str], **kwargs) -> Dict[str, str]:
    text = ' '.join(params)
    response = requests.get(
        url='https://api.duckduckgo.com/',
        params={'q': text, 'format': 'json'}
    )

    if 200 > response.status_code <= 300:
        raise RequestError(http_status=response.status_code)

    response = response.json()

    if not response['AbstractText']:
        raise NoResposeFound(keyword=text)

    return {
        'text': response['AbstractText'],
        'url': response['AbstractURL'],
        'source': response['AbstractSource']
    }


if __name__ == "__main__":
    process(text=['fsdfsdfsdfsdf'])
