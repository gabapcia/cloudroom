from dataclasses import dataclass


@dataclass
class ActionNotFound(Exception):
    activator: str

    def __str__(self):
        return f'The action for "{self.activator}" was not found'

@dataclass
class ModuleNotConfigured(Exception):
    name: str

    def __str__(self):
        return f'No module named "{self.name}" was found'

@dataclass
class InvalidCommand(Exception):
    command: str

    def __str__(self):
        return f'No command named "{self.command}" was found'
