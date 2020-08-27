import random
from typing import Dict, Any


def process(**kwargs) -> Dict[str, Any]:
    greetings = ['Hello, may I help you?', 'Hi! What do you need?']
    return {'speak': random.choice(greetings)}


if __name__ == "__main__":
    import os
    import json
    path = os.path.join(
        os.getcwd(),
        'config',
        'commands.json'
    )
    with open(path, 'rb') as f:
        config = json.load(f)
    process(config=config)
