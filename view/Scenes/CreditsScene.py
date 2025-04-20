import pygame
from view.components.Button import Button


class CreditsScene:
    def __init__(self, screen, font, set_application_status):
        self.screen = screen
        self.font = font
        self.screen_width, self.screen_height = screen.get_size()
        self.set_application_status = set_application_status
        self.back_button = Button("Powrót do Menu",(self.screen_width // 2 - 200, self.screen_height - 150),(400, 100),self.back_to_menu,self.font)


        self.background = pygame.image.load("resources/menu.png").convert()
        self.background = pygame.transform.scale(self.background, (self.screen_width, self.screen_height))

        self.darken = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        self.darken.fill((0, 0, 0, 150))


    def draw(self):
        self.screen.blit(self.background, (0, 0))
        self.screen.blit(self.darken, (0, 0))
        credits_text = [
            "Autorzy:",
            "Krzysztof Pieczka",
            "Maciej Kus"
        ]

        y_pos = self.screen_height // 2 - 80

        for line in credits_text:
            text = self.font.render(line, True, (255, 255, 255))
            text_rect = text.get_rect(center=(self.screen_width // 2, y_pos))
            self.screen.blit(text, text_rect)
            y_pos += 50

        self.back_button.draw(self.screen)
        self.back_button.on_hover(pygame.mouse.get_pos())

    def handle_events(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.back_button.check_click(event.pos)

    def back_to_menu(self):
        self.set_application_status("menu")