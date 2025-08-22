from overrides import overrides

from src.model.abilities.commanders.commander_base import CommanderAbilityBase
from src.model.enums.ability_type import AbilityType
from src.presenter.settings import locale as l


class GiveChooseGrave(CommanderAbilityBase):
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
        grave = player.grave
        opponent_grave = opponent.grave

        if hand.size() < 1 or grave.size() + opponent_grave.size() < 1:
            return actions

        graves = opponent.get_grave_cards(playable_only=True)
        graves.extend(player.get_grave_cards(playable_only=True))
        actions.append(lambda: self.carousel(presenter, hand.cards, 1, False,
                                             l("Choose a card to donate.")))
        actions.append(lambda: self.carousel(presenter, graves, 1, True,
                                             l("Choose 1 card from the discard piles.")))
        return actions

    @staticmethod
    def carousel(presenter, cards, count, allow_ending, label):
        presenter.show_carousel(cards, choose_count=count, cancelable=False, allow_ending=allow_ending, label=label)

    @overrides
    def on_board_play(self, game, player, row_type, targets):
        if len(targets) < 2:
            return

        opponent = game.get_player(1 - player.id)

        target_id = targets.pop(0)
        card = player.get_from_hand(target_id)
        if card is None:
            raise ValueError(f"Wrong commander use: cannot find target {target_id} in p{player.id}")
        opponent.hand.add_card(card)

        target_id = targets.pop(0)
        target = opponent.grave.find_card_by_id(target_id)
        if target:
            opponent.grave.remove_card(target)
            player.hand.add_card(target)
            return

        target = player.grave.find_card_by_id(target_id)
        if target is None:
            raise ValueError(f"Wrong commander use: cannot find target {target_id} in graves")

        player.grave.remove_card(target)
        player.hand.add_card(target)