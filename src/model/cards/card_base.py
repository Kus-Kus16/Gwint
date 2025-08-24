from abc import ABC

from src.model.enums.faction_type import FactionType

class CardBase(ABC):
    def __init__(self, data):
        self.id = data['id']
        self.name = data['name']
        self.faction = FactionType(data['faction'])
        self.owner = None
        self.filename = data['filename']
        self.type = None
        self.ability_types = set()
        self.abilities = self.create_abilities(data['abilities'])

    def add_types(self, types):
        self.ability_types.update(types)

    def create_abilities(self, strings):
        from src.model.abilities.ability_base import ABILITY_REGISTRY
        def to_class_name(snake_name):
            return ''.join(word.capitalize() for word in snake_name.split('_'))

        instances = []
        for snake_name in strings:
            class_name = to_class_name(snake_name)
            cls = ABILITY_REGISTRY[class_name]
            instances.append(cls(self))

        return instances

    def is_card_type(self, card_type):
        return self.type == card_type

    def is_ability_type(self, ability_type):
        return ability_type in self.ability_types

    def is_row_playable(self, row_type):
        return True