import os
import json
import string
import random
import nltk
from importlib import import_module
from typing import Dict, Any, List, Callable, Generator
from . import modules
from .utils.exceptions import ActionNotFound, ModuleNotConfigured
nltk.download('punkt')
nltk.download('stopwords')


class Engine:
    APOLOGY_MESSAGES = ["Sorry, I didn't understant."]

    def __init__(self, *, config_dir: str = None):
        self.config_dir = config_dir or os.getenv(
            'CHRISTINE_CONFIG_PATH',
            os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config')
        )
        self.config = self.__get_config()

    def __get_config(self) -> Dict[str, Any]:
        path = os.path.join(self.config_dir, 'commands.json')

        with open(path, 'rb') as f:
            config = json.load(f)

        return config

    def __get_process_method(self, module:  str) -> Callable:
        try:
            module = import_module(f'{modules.__package__}.{module}.main')
        except ModuleNotFoundError:
            raise ModuleNotConfigured(name=module)

        return module.process

    def __parse_user_input(
        self,
        text: str,
        only_params: bool = False
    ) -> List[Any]:
        tokens = [
            word
            for word in nltk.word_tokenize(text.lower())
            if word not in string.punctuation
        ]

        return tokens if only_params else (tokens[0], tokens[1:])

    def __get_module(self, activator: str) -> str:
        for module, configs in self.config.items():
            if activator in configs['activators']:
                return module, configs['default']

        raise ActionNotFound(activator=activator)

    def process(self, text: str) -> Generator:
        activator, params = self.__parse_user_input(text=text)
        try:
            module, default_messages = self.__get_module(activator=activator)
        except ActionNotFound:
            yield {'result': {'speak': random.choice(Engine.APOLOGY_MESSAGES)}}
            return

        if not params and default_messages:
            text = yield {'request': {'speak': random.choice(default_messages)}}
            params = self.__parse_user_input(text, only_params=True)

        module_process = self.__get_process_method(module=module)

        yield {'result': module_process(params=params, config=self.config)}
