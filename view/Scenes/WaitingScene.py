import pygame

from view.components.Button import Button


class WaitingScene:
    def __init__(self, screen, font, application_status):
        self.screen = screen
        self.font = font
        self.screen_width, self.screen_height = screen.get_size()
        self.application_status = application_status

        self.back_button = Button("Powrót do Menu", (self.screen_width // 2 - 200, self.screen_height - 150),
                                  (400, 100), self.back_to_menu, self.font)

        self.background = pygame.image.load("resources/menu.png").convert()
        self.background = pygame.transform.scale(self.background, (self.screen_width, self.screen_height))

        self.darken = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        self.darken.fill((0, 0, 0, 150))

    def draw(self):
        self.screen.blit(self.background, (0, 0))
        self.screen.blit(self.darken, (0, 0))

        text = self.font.render("Oczekiwanie na przeciwnika", True, (255, 255, 255))
        text_rect = text.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
        self.screen.blit(text, text_rect)

        self.back_button.draw(self.screen)
        self.back_button.on_hover(pygame.mouse.get_pos())


    def handle_events(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.back_button.check_click(event.pos)

    def back_to_menu(self):
        self.application_status("menu")
