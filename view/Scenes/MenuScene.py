import pygame
from view.components.Button import Button
from view.components.VolumeSlider import VolumeSlider


class MenuScene:
	def __init__(self, screen, font, application_status):
		self.screen = screen
		self.font = font
		self.screen_width, self.screen_height = screen.get_size()
		self.application_status = application_status
		self.menu_buttons = [
			Button("Nowa gra", (self.screen_width // 2 - 200, self.screen_height // 2), (400, 80), self.start_game, font),
			Button("Autorzy", (self.screen_width // 2 - 200, self.screen_height // 2 + 100), (400, 80), self.show_credits, font),
			Button("Twoja talia", (self.screen_width // 2 - 200, self.screen_height // 2 + 200), (400, 80), self.end_game, font),
			Button("Wyjście", (self.screen_width // 2 - 200, self.screen_height // 2 + 300), (400, 80), self.end_game, font)

		]
		self.background = pygame.image.load("resources/menu.png")
		self.background = pygame.transform.scale(self.background, (self.screen_width, self.screen_height))


	def draw(self):
		self.screen.blit(self.background, (0, 0))
		mouse_pos = pygame.mouse.get_pos()
		for btn in self.menu_buttons:
			btn.draw(self.screen)
			btn.on_hover(mouse_pos)


	def handle_events(self, event):
		if event.type == pygame.MOUSEBUTTONDOWN:
			for btn in self.menu_buttons:
				btn.check_click(event.pos)

	def start_game(self):
		self.application_status("waiting-for-game")

	def end_game(self):
		self.application_status("exit")

	def show_credits(self):
		self.application_status("credits")