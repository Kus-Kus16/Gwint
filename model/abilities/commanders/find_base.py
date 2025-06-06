from abc import ABC

from overrides import overrides

from model.abilities.commanders.commander_base import CommanderAbilityBase
from model.enums.row_type import RowType


class FindBase(CommanderAbilityBase, ABC):
    def __init__(self, card, seeked_id):
        super().__init__(card)
        self.seeked_id = seeked_id

    @overrides
    def on_board_play(self, game, player, row_type, targets):
        card = player.get_from_deck(self.seeked_id)
        if card is not None:
            game.play_extra_card(player.id, card, RowType.ANY)