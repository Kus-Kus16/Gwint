import copy
from overrides import overrides

from src.model.abilities.commanders.commander_base import CommanderAbilityBase
from src.model.card_holders.row import Row
from src.model.enums import ability_type
from src.model.enums.row_type import RowType


class Optimise(CommanderAbilityBase):
    @overrides
    def on_board_play(self, game, player, row_type, targets):
        row_close, _ = game.board.get_row(RowType.CLOSE, player.id)
        row_range, _ = game.board.get_row(RowType.RANGED, player.id)
        fake_row_close = Row()
        fake_row_range = Row()

        fake_row_close.effects["weather"] = row_close.effects["weather"]
        fake_row_range.effects["weather"] = row_range.effects["weather"]
        fake_row_close.effects["morale"] = copy.deepcopy(row_close.effects["morale"])
        fake_row_range.effects["morale"] = copy.deepcopy(row_range.effects["morale"])

        cards = []
        demorale_idx = -1

        for card in list(row_close.cards):
            if card.is_ability_type(ability_type.AbilityType.AGILE):
                if card.is_ability_type(ability_type.AbilityType.DEMORALIZING):
                    demorale_idx += 1
                    cards.insert(demorale_idx, card)
                elif card.is_ability_type(ability_type.AbilityType.MORALIZING):
                    cards.insert(demorale_idx + 1, card)
                else:
                    cards.append(card)
                row_close.cards.remove(card)
        for card in list(row_range.cards):
            if card.is_ability_type(ability_type.AbilityType.AGILE):
                if card.is_ability_type(ability_type.AbilityType.DEMORALIZING):
                    demorale_idx += 1
                    cards.insert(demorale_idx, card)
                elif card.is_ability_type(ability_type.AbilityType.MORALIZING):
                    cards.insert(demorale_idx + 1, card)
                else:
                    cards.append(card)
                row_range.cards.remove(card)

        for card in cards:
            maxi = -1
            row = None

            fake_row_close.add_card(card)
            if fake_row_close.cards[0].power > maxi:
                maxi = fake_row_close.cards[0].power
                row = row_close
            fake_row_close.remove_card(card)

            fake_row_range.add_card(card)
            if fake_row_range.cards[0].power > maxi:
                maxi = fake_row_range.cards[0].power
                row = row_range
            fake_row_range.remove_card(card)

            row.add_card(card)

        return