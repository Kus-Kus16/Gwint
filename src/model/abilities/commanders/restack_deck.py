from overrides import overrides

from src.model.abilities.commanders.commander_base import CommanderAbilityBase
from src.model.enums.ability_type import AbilityType
from src.presenter.settings import locale as l


class RestackDeck(CommanderAbilityBase):
    @overrides
    def get_types(self):
        types = super().get_types()
        types.extend([AbilityType.CHOOSING])
        return types

    @overrides
    def on_carousel_request(self, presenter):
        actions = []

        player = presenter.game.get_player(presenter.my_id)
        deck = player.deck

        if deck.size() < 1:
            return actions

        cards = deck.cards[:3]

        actions.append(lambda: self.carousel(presenter, cards, 3))
        return actions

    @staticmethod
    def carousel(presenter, cards, count):
        presenter.show_carousel(cards, choose_count=count, cancelable=False,
                                label=l("Put the cards back on the deck."))

    @overrides
    def on_board_play(self, game, player, row_type, targets):
        if len(targets) < 3:
            return

        deck = player.deck
        for _ in range(3):
            target_id = targets.pop(0)
            target = deck.find_card_by_id(target_id)
            if target is None:
                raise ValueError(f"Wrong commander use: cannot find target {target_id} in p{player.id}")

            deck.remove_card(target)
            deck.put_on_top(target)