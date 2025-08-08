from src.model.card_holders.row import Row
from src.model.card_holders.weather import Weather
from src.model.enums.weather_type import WeatherType


class Board:
    def __init__(self):
        #ROWS: 0close, 0ranged, 0siege, 1close, 1ranged, 1siege
        self.rows = [Row() for _ in range(6)]
        self.weather = Weather()

    @classmethod
    def row_index(cls, row_type, player_id):
        row_index = row_type.value
        if player_id == 1:
            row_index = (row_index + 3) % 6

        row_player_id = 0 if row_index < 3 else 1
        return row_index, row_player_id

    def get_row(self, row_type, player_id):
        row_index, row_player_id = self.row_index(row_type, player_id)
        return self.rows[row_index], row_player_id

    def play_card(self, card, row_type, player_id):
        row_index, _ = self.row_index(row_type, player_id)
        row = self.rows[row_index]
        row.add_card(card)

    def rows_sum(self):
        return sum(self.rows[i].points for i in range(3)), sum(self.rows[i].points for i in range(3, 6))

    def add_weather(self, card, weather, player_id):
        self.weather.add_card(card)
        weather_type = weather.weather_type

        if weather_type == WeatherType.CLEAR:
            self.clear_weather()
            return

        self.weather.put(weather_type)
        for row_type in weather.get_affected_rows():
            i, _ = self.row_index(row_type, player_id)
            self.rows[i].add_weather()

    def clear_weather(self):
        self.weather.clear()

        for row in self.rows:
            row.clear_weather()

    def is_weather_active(self, weather_type):
        return self.weather.contains(weather_type)

    def update_rows(self):
        for row in self.rows:
            row.recalculate()

    def clear_rows(self, players):
        player0, player1 = players
        add = []

        for i in range(0, 3):
            add += self.rows[i].clear(player0)
            self.rows[i].clear_boosts()

        for i in range(3, 6):
            add += self.rows[i].clear(player1)
            self.rows[i].clear_boosts()

        return add

    def get_ordered_rows(self, player_id):
        rows0 = self.rows[0:3]
        rows1 = self.rows[3:6]

        if player_id == 0:
            return rows1[::-1] + rows0
        else:
            return rows0[::-1] + rows1

    def scorch_row(self, row_type, player_id):
        row_index, row_player_id = self.row_index(row_type, player_id)
        row = self.rows[row_index]
        scorched = []

        if row.points < 10:
            return scorched

        cards = row.find_strongest(ignore_heroes=True)
        for card in cards:
            row.remove_card(card)
            scorched.append((card, row_player_id))

        return scorched

    def scorch(self):
        maxi = -10e10
        all_cards = [[] for _ in range(6)]
        scorched = []

        for i, row in enumerate(self.rows):
            cards = row.find_strongest(ignore_heroes=True)
            if len(cards) > 0 and cards[0].power >= maxi:
                if cards[0].power > maxi:
                    maxi = cards[0].power
                    all_cards = [[] for _ in range(6)]

                all_cards[i] = cards

        for i, row in enumerate(self.rows):
            row_player_id = 0 if i < 3 else 1
            for card in all_cards[i]:
                row.remove_card(card)
                scorched.append( (card, row_player_id) )

        self.update_rows()
        return scorched

    def scorch_low(self, player_id):
        rows = self.rows[player_id * 3 : (player_id + 1) * 3]
        mini = 10e6
        all_cards = [[] for _ in range(3)]
        scorched = []

        for i, row in enumerate(rows):
            cards = row.find_weakest(ignore_heroes=True)
            if len(cards) > 0 and cards[0].power <= mini:
                if cards[0].power < mini:
                    mini = cards[0].power
                    all_cards = [[] for _ in range(3)]

                all_cards[i] = cards

        for i, row in enumerate(rows):
            for card in all_cards[i]:
                row.remove_card(card)
                scorched.append((card, player_id))

        self.update_rows()
        return scorched
