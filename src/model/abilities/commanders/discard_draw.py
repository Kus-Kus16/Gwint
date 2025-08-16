from overrides import overrides

from src.model.abilities.commanders.choose_base import ChooseBase


class DiscardDraw(ChooseBase):
    @overrides
    def get_carousel_cards(self, presenter):
        player = presenter.game.get_player(presenter.my_id)
        return player.hand.cards

    @overrides
    def on_board_play(self, game, player, row_type, targets):
        if len(targets) == 0:
            return

        hand = game.get_player(player.id).hand
        target = self.find_target(targets, player, hand)

        hand.remove_card(target)
        player.send_to_grave(target)
        player.draw_cards(2)