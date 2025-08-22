from overrides import overrides

from src.model.abilities.commanders.commander_base import CommanderAbilityBase
from src.model.enums.ability_type import AbilityType
from src.presenter.settings import locale as l


class DiscardChoose(CommanderAbilityBase):
    @overrides
    def get_types(self):
        types = super().get_types()
        types.extend([AbilityType.CHOOSING])
        return types

    @overrides
    def on_carousel_request(self, presenter):
        actions = []

        player = presenter.game.get_player(presenter.my_id)
        hand = player.hand
        deck = player.deck

        if hand.size() < 2 or deck.size() < 1:
            return actions

        actions.append(lambda: self.carousel(presenter, hand.cards, 2, False,
                                             l("Choose 2 cards to discard.")))
        actions.append(lambda: self.carousel(presenter, presenter.game.shuffle_cards(deck), 1, True,
                                             l("Choose 1 card from your deck.")))
        return actions

    @staticmethod
    def carousel(presenter, cards, count, allow_ending, label):
        presenter.show_carousel(cards, choose_count=count, cancelable=False, allow_ending=allow_ending, label=label)

    @overrides
    def on_board_play(self, game, player, row_type, targets):
        if len(targets) < 3:
            return

        for _ in range(2):
            target_id = targets.pop(0)
            card = player.get_from_hand(target_id)
            if card is None:
                raise ValueError(f"Wrong commander use: cannot find target {target_id} in p{player.id}")
            player.send_to_grave(card)

        deck = player.deck
        hand = player.hand

        target_id = targets.pop(0)
        target = deck.find_card_by_id(target_id)
        if target is None:
            raise ValueError(f"Wrong commander use: cannot find target {target_id} in p{player.id}")

        deck.remove_card(target)
        hand.add_card(target)