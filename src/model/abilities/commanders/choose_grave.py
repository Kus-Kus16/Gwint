from overrides import overrides

from src.model.abilities.commanders.choose_base import ChooseBase


class ChooseGrave(ChooseBase):
    @overrides
    def get_carousel_cards(self, presenter):
        player = presenter.game.get_player(presenter.my_id)
        return player.get_grave_cards(playable_only=True)

    @overrides
    def on_board_play(self, game, player, row_type, targets):
        if len(targets) == 0:
            return

        grave = game.get_player(player.id).grave
        target_id = targets.pop(0)
        target = grave.find_card_by_id(target_id)
        if target is None:
            raise ValueError(f"Wrong commander use: cannot find target {target_id} in p{player.id}")

        grave.remove_card(target)
        player.hand.add_card(target)