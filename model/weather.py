from model.card_holder import CardHolder


class Weather(CardHolder):
    def __init__(self):
        super().__init__()
        self.active = set()

    def contains(self, weather_ability):
        return weather_ability in self.active

    def clear(self):
        for card in self.cards:
            card.send_to_owner_grave()

        self.cards.clear()
        self.active.clear()

    def put(self, weather_ability):
        self.active.add(weather_ability)