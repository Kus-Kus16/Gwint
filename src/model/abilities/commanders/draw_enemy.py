from overrides import overrides

from src.model.abilities.commanders.commander_base import CommanderAbilityBase


class DrawEnemy(CommanderAbilityBase):
    @overrides
    def on_board_play(self, game, player, row_type, targets):
        opponent = game.get_player(1 - player.id)
        hand = player.hand
        opponent_deck = opponent.deck

        extra = opponent_deck.get_next_card()
        if extra:
            hand.add_card(extra)