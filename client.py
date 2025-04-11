import time

import pygame
from network.network import Network

def main():
    pygame.init()
    width, height = 800, 500
    win = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Client")
    clock = pygame.time.Clock()
    game_started = False
    try:
        n = Network()
        color = (255, 255, 255)

        try:
            response = n.send("connect")
            if response:
                player_id = int(response)
                print(f"Jesteś graczem {player_id}")
            else:
                raise ValueError("Brak odpowiedzi")
        except Exception as e:
            print(f"Błąd podczas uzyskiwania ID gracza: {e}")
            pygame.quit()
            return

        font = pygame.font.SysFont('Arial', 30) if pygame.font.get_fonts() else pygame.font.Font(None, 30)

        while True:
            clock.tick(60)
            time.sleep(1)
            # Sprawdź status gry
            try:
                if game_started:
                    game = n.send("get_game")
                    #text = font.render(current_player, True, (0, 0, 0))
                    print(game.game_tostring(player_id))
                    if game.current_player_id is None:
                        print(game.round_history)
                        return

                    if game.current_player_id == player_id:
                        print("\n Enter card id: ")
                        card_id = int(input())
                        print("\n Enter row (close, ranged, siege): ")
                        row = input()
                        tmp = n.send(f"{card_id}:{row}")
                else:
                    text = font.render(f"Jesteś graczem {player_id}", True, (0, 0, 0))

                    status = n.send("status")

                    if status == "game_started":
                        game_started = True
                        color = (0, 255, 0)  # Zielony - gra rozpoczęta
                    else:
                        color = (255, 0, 0)  # Czerwony - czekanie na drugiego gracza
            except Exception as e:
                print(f"Błąd komunikacji: {e}")
                break

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return

            win.fill(color)

            win.blit(text, (50, height // 2))

            pygame.display.update()

    except Exception as e:
        print(f"Krytyczny błąd: {e}")
    pygame.quit()

main()