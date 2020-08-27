from typing import Dict, Any


def process(**kwargs) -> Dict[str, Any]:
    config = kwargs['config']

    doc = {}
    for module, option in config.items():
        activators = '", "'.join(option['activators'][:-1])

        if activators:
            activators = '" or "'.join([activators, option['activators'][-1]])
        else:
            activators = option['activators'][-1]

        doc[module] = f'{option["description"]}. To activate say "{activators}"'

    return doc


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
