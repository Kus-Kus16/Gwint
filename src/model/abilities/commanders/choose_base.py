from abc import ABC, abstractmethod

from overrides import overrides

from src.model.abilities.commanders.commander_base import CommanderAbilityBase
from src.model.enums.ability_type import AbilityType


class ChooseBase(CommanderAbilityBase, ABC):
    @overrides
    def get_types(self):
        types = super().get_types()
        types.extend([AbilityType.CHOOSING])
        return types

    @overrides
    def on_carousel_request(self, presenter):
        actions = []

        cards = self.get_carousel_cards(presenter)
        if cards:
            actions.append(lambda: self.carousel(presenter, cards))

        return actions

    @classmethod
    def carousel(cls, presenter, cards):
        presenter.show_carousel(cards, choose_count=1, cancelable=False)

    @abstractmethod
    def get_carousel_cards(self, presenter):
        return []