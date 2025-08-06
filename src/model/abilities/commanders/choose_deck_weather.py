from overrides import overrides

from src.model.abilities.commanders.commander_base import CommanderAbilityBase
from src.model.enums.ability_type import AbilityType
from src.model.enums.row_type import RowType


class ChooseDeckWeather(CommanderAbilityBase):
    @overrides
    def get_types(self):
        types = super().get_types()
        types.extend([AbilityType.CHOOSING])
        return types

    @overrides
    def on_carousel_request(self, presenter):
        actions = []

        deck = presenter.game.get_player(presenter.my_id).deck
        cards = deck.filter_cards(AbilityType.WEATHER)
        if cards:
            actions.append(lambda: self.carousel(presenter, cards))

        return actions

    @classmethod
    def carousel(cls, presenter, cards):
        presenter.show_carousel(cards, choose_count=1, cancelable=False)

    @overrides
    def on_board_play(self, game, player, row_type, targets):
        if len(targets) == 0:
            return

        deck = player.deck
        target_id = targets.pop(0)
        target = deck.find_card_by_id(target_id)
        if target is None:
            raise ValueError(f"Wrong commander use: cannot find target {target_id} in p{player.id}")

        deck.remove_card(target)
        game.play_extra_card(player.id, target, RowType.ANY)