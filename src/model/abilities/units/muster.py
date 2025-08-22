from overrides import overrides

from src.model.cards.cards_database import CardsDatabase
from src.model.abilities.units.unit_base import UnitAbilityBase


class Muster(UnitAbilityBase):
    @overrides
    def on_board_play(self, game, player, row_type, targets):
        actions = []
        card_id = self.card.id
        other_ids = CardsDatabase.get_muster(card_id)

        for id in other_ids:
            extra = player.get_from_hand(id, excluding=self.card) or player.get_from_deck(id)
            if extra is not None:
                actions.append(lambda e=extra, r=extra.rows[0]: self.muster(game, player, e, r))

        return actions

    @staticmethod
    def muster(game, player, extra_card, row_type):
        game.play_extra_card(player.id, extra_card, row_type)