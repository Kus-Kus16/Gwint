from overrides import overrides

from model.abilities.commanders.commander_base import CommanderAbilityBase
from model.enums.ability_type import AbilityType


class ChooseEnemyGrave(CommanderAbilityBase):
    @overrides
    def get_types(self):
        types = super().get_types()
        types.extend([AbilityType.CHOOSING])
        return types

    @overrides
    def on_carousel_request(self, presenter):
        actions = []

        cards = presenter.game.get_player(1 - presenter.my_id).get_grave_cards(playable_only=True)
        if cards:
            actions.append(lambda: self.carousel(presenter, cards))

        return actions

    @classmethod
    def carousel(cls, presenter, cards):
        presenter.show_carousel(cards, choose_count=1, cancelable=False)

    @overrides
    def on_board_play(self, game, player, row_type, targets):
        if len(targets) == 0:
            return

        opponent_id = 1 - player.id
        grave = game.get_player(opponent_id).grave
        target_id = targets.pop(0)
        target = grave.find_card_by_id(target_id)
        if target is None:
            raise ValueError(f"Wrong commander use: cannot find target {target_id} in p{opponent_id}")

        grave.remove_card(target)
        player.hand.add_card(target)