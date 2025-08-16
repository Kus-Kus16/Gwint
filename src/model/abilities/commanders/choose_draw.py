from overrides import overrides

from src.model.abilities.commanders.choose_base import ChooseBase


class ChooseDraw(ChooseBase):
    @overrides
    def get_carousel_cards(self, presenter):
        player = presenter.game.get_player(presenter.my_id)
        return player.deck.cards[:3]

    @overrides
    def on_board_play(self, game, player, row_type, targets):
        if len(targets) == 0:
            return

        deck = game.get_player(player.id).deck
        target = self.find_target(targets, player, deck)

        deck.remove_card(target)
        player.hand.add_card(target)