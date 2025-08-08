from abc import ABC

from overrides import overrides

from src.model.abilities.commanders.commander_base import CommanderAbilityBase
from src.model.enums.row_type import RowType


class ReshuffleGraves(CommanderAbilityBase):
    @overrides
    def on_board_play(self, game, player, row_type, targets):
        opponent = game.get_player(1 - player.id)
        player.grave.transfer_all_cards(player.deck)
        opponent.grave.transfer_all_cards(opponent.deck)
        game.shuffle_decks()
