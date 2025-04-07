import pygame
import socket
import time
from network.network import Network

def main():
    pygame.init()
    width, height = 800, 500
    win = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Client")
    clock = pygame.time.Clock()

    try:
        n = Network()
        color = (255, 255, 255)
        player_id = None
        game_started = False

        # Pierwsza wiadomość - pobierz ID gracza
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

            # Sprawdź status gry
            try:
                status = n.send("status")

                if status == "game_started":
                    game_started = True
                    color = (0, 255, 0)  # Zielony - gra rozpoczęta
                elif status and status.isdigit():
                    if int(status) == 2:
                        color = (0, 0, 255)  # Niebieski - dwóch graczy
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

            # Wyświetl informacje o stanie gry
            if game_started:
                text = font.render(f"Jesteś graczem {player_id}", True, (0, 0, 0))
            elif player_id is not None:
                text = font.render(f"Jesteś graczem {player_id}", True, (0, 0, 0))
            else:
                text = font.render("Łączenie z serwerem...", True, (0, 0, 0))

            win.blit(text, (50, height // 2))

            pygame.display.update()

    except Exception as e:
        print(f"Krytyczny błąd: {e}")
    pygame.quit()

main()