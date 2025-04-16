class ConsoleView:
    def show_game(self, game, player_id):
        print("\n\n" + str(game.players[1- player_id]) + "\n\n")
        print(game.to_string(player_id))

    def show_game_history(self, game):
        print(game.round_history)

    def get_card_input(self):
        print("\n Enter card id: ")
        card_id = int(input())
        print("\n Enter row (close, ranged, siege): ")
        row = input()

        return card_id, row

    def get_rematch(self):
        print("\nExit / Rematch?")
        return input().lower() == "rematch"

    def show_error(self, error):
        print(error)
