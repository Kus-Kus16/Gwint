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

    @staticmethod
    def carousel(presenter, cards):
        presenter.show_carousel(cards, choose_count=1, cancelable=False)

    @staticmethod
    def find_target(targets, player, container):
        target_id = targets.pop(0)
        target = container.find_card_by_id(target_id)
        if target is None:
            raise ValueError(f"Wrong commander use: cannot find target {target_id} in p{player.id}")
        return target

    @abstractmethod
    def get_carousel_cards(self, presenter):
        return []