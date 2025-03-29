from classes.Row import Row
from classes.Weather import Weather


class Board:
    def __init__(self):
        #ROWS: 0close, 0ranged, 0siege, 1close, 1ranged, 1siege
        self.rows = [Row() for _ in range(6)]
        self.weather = Weather()

    def play_card(self, card, row_type, player_id):
        row_index = row_type.value

        if player_id == 1:
            row_index += 3

        row = self.rows[row_index]
        row.add_card(card)
        row.recalculate()

    def rows_sum(self):
        return sum(self.rows[i].points for i in range(3)), sum(self.rows[i].points for i in range(3, 6))

    def add_weather(self, card, weather_ability):
        rows_map = {
            "frost": [0, 3],
            "fog": [1, 4],
            "rain": [2, 5],
            "storm": [1, 4, 2, 5],
        }

        self.weather.add_card(card)

        if weather_ability == "clear":
            self.weather.clear()

            for row in self.rows:
                row.clear_weather()
        else:
            self.weather.put(weather_ability)
            for index in rows_map[weather_ability]:
                self.rows[index].add_weather()


    def is_weather_active(self, weather_ability):
        return self.weather.contains(weather_ability)

    def update_rows(self):
        for row in self.rows:
            row.recalculate()

    def rows_tostring(self, player_id):
        rows0 = self.rows[0:3]
        rows1 = self.rows[3:6]

        if player_id == 0:
            rows1.reverse()
            return "\n".join(str(row) for row in rows1) + "\n" + "\n".join(str(row) for row in rows0) + "\n"

        rows0.reverse()
        return "\n".join(str(row) for row in rows0) + "\n" + "\n".join(str(row) for row in rows1) + "\n"