from overrides import overrides

from src.model.abilities.commanders.commander_base import CommanderAbilityBase


class ShowEnemy(CommanderAbilityBase):
    @overrides
    def on_board_play(self, game, player, row_type, targets):
        opponent_id = 1 - player.id
        card_holder = game.get_player(opponent_id).hand
        cards = game.shuffle_cards(card_holder)
        return cards[:3]