from overrides import overrides

from src.model.abilities.commanders.choose_base import ChooseBase
from src.model.abilities.commanders.commander_base import CommanderAbilityBase
from src.model.enums.ability_type import AbilityType
from src.model.enums.row_type import RowType


class ChooseDeckWeather(ChooseBase):
    @overrides
    def get_carousel_cards(self, presenter):
        player = presenter.game.get_player(presenter.my_id)
        return player.deck.filter_cards(AbilityType.WEATHER)

    @overrides
    def on_board_play(self, game, player, row_type, targets):
        if len(targets) == 0:
            return

        deck = player.deck
        target = self.find_target(targets, player, deck)

        deck.remove_card(target)
        game.play_extra_card(player.id, target, RowType.ANY)