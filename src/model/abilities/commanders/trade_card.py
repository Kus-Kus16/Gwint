from overrides import overrides

from src.model.abilities.commanders.commander_base import CommanderAbilityBase
from src.model.enums.ability_type import AbilityType


class TradeCard(CommanderAbilityBase):
    @overrides
    def get_types(self):
        types = super().get_types()
        types.extend([AbilityType.CHOOSING])
        return types

    @overrides
    def on_carousel_request(self, presenter):
        actions = []

        player = presenter.game.get_player(presenter.my_id)
        opponent = presenter.game.get_player(1 - presenter.my_id)
        hand = player.hand
        opponent_hand = opponent.hand

        if hand.size() < 1 or opponent_hand.size() < 1:
            return actions

        actions.append(lambda: self.carousel(presenter, hand.cards, 1))
        return actions

    @staticmethod
    def carousel(presenter, cards, count):
        presenter.show_carousel(cards, choose_count=count, cancelable=False)

    @overrides
    def on_board_play(self, game, player, row_type, targets):
        if not targets:
            return

        opponent = game.get_player(1 - player.id)
        hand = player.hand
        opponent_hand = opponent.hand

        target_id = targets.pop(0)
        target = hand.find_card_by_id(target_id)
        if target is None:
            raise ValueError(f"Wrong commander use: cannot find target {target_id} in p{player.id}")

        cards = game.shuffle_cards(opponent_hand)
        extra = cards[0]

        hand.remove_card(target)
        opponent_hand.remove_card(extra)
        hand.add_card(extra)
        opponent_hand.add_card(target)
