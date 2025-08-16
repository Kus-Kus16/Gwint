from overrides import overrides

from src.model.abilities.commanders.choose_base import ChooseBase


class ChooseEnemyGrave(ChooseBase):
    @overrides
    def get_carousel_cards(self, presenter):
        player = presenter.game.get_player(1 - presenter.my_id)
        return player.get_grave_cards(playable_only=True)

    @overrides
    def on_board_play(self, game, player, row_type, targets):
        if len(targets) == 0:
            return

        opponent_id = 1 - player.id
        grave = game.get_player(opponent_id).grave
        target = self.find_target(targets, player, grave)

        grave.remove_card(target)
        player.hand.add_card(target)