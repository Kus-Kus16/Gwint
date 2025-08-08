from overrides import overrides

from src.model.abilities.specials.special_base import SpecialAbilityBase
from src.model.enums.ability_type import AbilityType
from src.model.enums.card_type import CardType

def decoy(game, player, row_type, targets, card, card_type):
    player_id = player.id
    target_id = targets.pop(0)

    row, row_owner_id = game.board.get_row(row_type, player_id)
    if row_owner_id != player_id:
        raise ValueError(f"Wrong {card_type} use: row_owner_id:{row_owner_id} does not match p{player_id}")

    target = row.find_card_by_id(target_id)
    if target is None:
        raise ValueError(f"Wrong {card_type} use: cannot find target {target_id} for p{player_id}")
    if not target.is_card_type(CardType.UNIT):
        raise ValueError(f"Wrong {card_type} use: target {target_id} is not a unit")

    row.add_card(card)
    row.remove_card(target)
    player.hand.add_card(target)

class Decoy(SpecialAbilityBase):
    @overrides
    def get_types(self):
        return [AbilityType.TARGETING]

    @overrides
    def on_board_play(self, game, player, row_type, targets):
        decoy(game, player, row_type, targets, self.card, "decoy")