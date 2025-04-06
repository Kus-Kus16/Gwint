import pygame
from network import Network

pygame.init()

width = 500
height = 500
win = pygame.display.set_mode((width, height))
pygame.display.set_caption("Client")

font = pygame.font.SysFont("comicsans", 50)

class Player:
    def __init__(self, counter=0):
        self.counter = counter

    def draw(self, win):
        win.fill((255, 255, 255))
        text = font.render(f"Counter: {self.counter}", True, (0, 0, 0))
        win.blit(text, (150, 200))
        pygame.display.update()

    def update_counter(self, value):
        self.counter = value

def main():
    run = True
    clock = pygame.time.Clock()
    player = Player()
    n = Network()

    while run:
        clock.tick(60)
        try:
            # Wysyłamy lokalny licznik
            data = n.send(str(player.counter))
            # Serwer zwraca dane w formacie "licznik,coś_innego"
            # Parsujemy pierwszą część jako licznik
            received_values = data.split(",")
            other_counter = int(received_values[0])
            player.update_counter(other_counter)
        except Exception as e:
            run = False
            print("Connection lost or error:", e)
            break

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            # Jeśli kliknięto lewy przycisk myszy, zwiększamy licznik
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                player.counter += 1

        player.draw(win)

    pygame.quit()

main()
