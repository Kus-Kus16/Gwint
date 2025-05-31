from model.card_holders.card_holder import CardHolder


class Weather(CardHolder):
    def __init__(self):
        super().__init__()
        self.active = set()

    def contains(self, weather_type):
        return weather_type in self.active

    def clear(self):
        for card in self.cards:
            card.send_to_owner_grave()

        self.cards.clear()
        self.active.clear()

    def put(self, weather_type):
        self.active.add(weather_type)