from overrides import overrides

from model.abilities.ability_base import AbilityType
from model.abilities.units.unit_base import UnitAbilityBase


class Medic(UnitAbilityBase):
    @overrides
    def get_types(self):
        return [AbilityType.CHOOSING]

    @overrides
    def on_carousel_request(self, presenter):
        actions = []
        game = presenter.game

        if game.gamerule("heal_random"):
            return actions

        cards = game.get_player(presenter.my_id).get_grave_cards(playable_only=True)
        if cards:
            actions.append(lambda: self.carousel(presenter, cards))

        return actions

    @classmethod
    def carousel(cls, presenter, cards):
        presenter.show_carousel(cards, choose_count=-1, cancelable=False)

    @overrides
    def on_board_play(self, game, player, row_type, targets):
        if game.gamerule("heal_random"):
            cards = player.get_grave_cards(playable_only=True)
            if not cards:
                targets = []
            else:
                target = game.rng.choice(cards).id
                targets = [target]

        if len(targets) == 0:
            return []

        grave = player.grave
        target_id = targets.pop(0)
        target = grave.find_card_by_id(target_id)
        if target is None:
            raise ValueError(f"Wrong medic use: cannot find target {target_id} for p{player.id}")

        actions = [lambda: self.medic(game, player, target, targets)]
        return actions

    @classmethod
    def medic(cls, game, player, medic_target, targets):
        player.grave.remove_card(medic_target)
        game.play_extra_card(player.id, medic_target, medic_target.rows[0], targets)