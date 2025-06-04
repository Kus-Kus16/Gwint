from overrides import overrides

from model.abilities.specials.special_base import SpecialAbilityBase
from model.enums.ability_type import AbilityType


class Horn(SpecialAbilityBase):
    @overrides
    def get_types(self):
        return [AbilityType.BOOST]

    @overrides
    def on_board_play(self, game, player, row_type, targets):
        player_id = player.id
        row, row_owner_id = game.board.get_row(row_type, player_id)

        if row_owner_id != player_id:
            raise ValueError(f"Wrong horn use: row_owner_id:{row_owner_id} does not match p{player_id}")
        if not row.add_horn(self.card):
            raise ValueError(f"Wrong horn use: cannot add for row {row_type}")