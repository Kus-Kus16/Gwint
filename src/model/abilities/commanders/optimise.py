from overrides import overrides

from src.model.abilities.commanders.commander_base import CommanderAbilityBase
from src.model.card_holders.row import Row
from src.model.enums import ability_type
from src.model.enums.row_type import RowType


class Optimise(CommanderAbilityBase):
    @overrides
    def on_board_play(self, game, player, row_type, targets):

        def copy(set_to_copy):
            copied_set = set()
            for element in set_to_copy:
                copied_set.add(element)
            return copied_set

        row_close, _ = game.board.get_row(RowType.CLOSE, player.id)
        row_range, _ = game.board.get_row(RowType.RANGED, player.id)
        rows = [row_close, row_range]
        cards = []
        demorale_idx = -1

        for row in rows:
            for card in list(row.cards):
                if card.is_ability_type(ability_type.AbilityType.AGILE):
                    if card.is_ability_type(ability_type.AbilityType.DEMORALIZING):
                        demorale_idx += 1
                        cards.insert(demorale_idx, card)
                    elif card.is_ability_type(ability_type.AbilityType.MORALIZING):
                        cards.insert(demorale_idx + 1, card)
                    else:
                        cards.append(card)
                    row.remove_card(card)

        fake_row_close = Row()
        fake_row_range = Row()
        fake_rows = [fake_row_close, fake_row_range]
        for i in range(len(fake_rows)):
            fake_rows[i].effects["weather"] = rows[i].effects["weather"]
            fake_rows[i].effects["morale"] = copy(rows[i].effects["morale"])
            fake_rows[i].effects["horn"] = copy(rows[i].effects["horn"])

        for card in cards:
            maxi = -1
            row_idx = None
            fake_row_points = [0,0]

            for i in range(len(fake_rows)):
                fake_rows[i].add_card(card)
                if fake_rows[i].points - fake_row_points[i] > maxi:
                    maxi = fake_rows[i].points - fake_row_points[i]
                    row_idx = i
            fake_rows[(row_idx + 1) % 2].remove_card(card)
            fake_row_points[row_idx] = fake_rows[row_idx].points

            rows[row_idx].add_card(card)

        return