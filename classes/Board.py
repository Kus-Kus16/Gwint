from classes.Row import Row


class Board:
    def __init__(self):
        #ROWS: 0close, 0ranged, 0siege, 1close, 1ranged, 1siege
        self.rows = [Row() for _ in range(6)]
        self.weather = set()

    def play_card(self, card, row_type, player_id):
        row_index = row_type.value

        if player_id == 1:
            row_index += 3

        row = self.rows[row_index]
        row.add_card(card)
        row.recalculate()

        return self.rows_sum()

    def rows_sum(self):
        return sum(self.rows[i].points for i in range(3)), sum(self.rows[i].points for i in range(3, 6))

    def rows_tostring(self, player_id):
        rows0 = self.rows[0:3]
        rows1 = self.rows[3:6]

        if player_id == 0:
            rows1.reverse()
            return "\n".join(str(row) for row in rows1) + "\n" + "\n".join(str(row) for row in rows0) + "\n"

        rows0.reverse()
        return "\n".join(str(row) for row in rows0) + "\n" + "\n".join(str(row) for row in rows1) + "\n"