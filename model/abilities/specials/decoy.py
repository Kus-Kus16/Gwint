from overrides import overrides

from model.abilities.specials.special_base import SpecialAbilityBase
from model.enums.ability_type import AbilityType
from model.enums.card_type import CardType


class Decoy(SpecialAbilityBase):
    @overrides
    def get_types(self):
        return [AbilityType.TARGETING]

    @overrides
    def on_board_play(self, game, player, row_type, targets):
        player_id = player.id
        target_id = targets.pop(0)

        row, row_owner_id = game.board.get_row(row_type, player_id)
        if row_owner_id != player_id:
            raise ValueError(f"Wrong decoy use: row_owner_id:{row_owner_id} does not match p{player_id}")

        target = row.find_card_by_id(target_id)
        if target is None:
            raise ValueError(f"Wrong decoy use: cannot find target {target_id} for p{player_id}")
        if not target.is_card_type(CardType.UNIT):
            raise ValueError(f"Wrong decoy use: target {target_id} is not a unit")

        row.add_card(self.card)
        row.remove_card(target)
        player.hand.add_card(target)