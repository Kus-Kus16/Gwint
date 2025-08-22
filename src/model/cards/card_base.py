import importlib
from abc import ABC

from src.model.enums.faction_type import FactionType


class CardBase(ABC):
    def __init__(self, data):
        self.id = data['id']
        self.name = data['name']
        self.faction = FactionType(data['faction'])
        self.owner = None
        self.filename = data['filename']
        self.abilities = None
        self.type = None
        self.ability_types = set()

    def add_types(self, types):
        self.ability_types.update(types)

    def create_abilities(self, strings, abilities_path):
        def to_class_name(snake_name):
            return ''.join(word.capitalize() for word in snake_name.split('_'))

        instances = []
        for snake_name in strings:
            class_name = to_class_name(snake_name)
            module_path = f"model.{abilities_path}.{snake_name}"

            module = importlib.import_module(module_path)
            cls = getattr(module, class_name)
            instances.append(cls(self))

        return instances

    def is_card_type(self, card_type):
        return self.type == card_type

    def is_ability_type(self, ability_type):
        return ability_type in self.ability_types

    def is_row_playable(self, row_type):
        return True