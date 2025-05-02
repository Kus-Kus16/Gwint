import pygame
from overrides import overrides

from view.Scenes.Scene import Scene
from view.components.Button import Button


class MenuScene(Scene):
	def __init__(self, screen, framerate, font):
		super().__init__(screen, framerate, font, "resources/menu.png")

		button_x = self.screen_width // 2 - 200
		button_y = self.screen_height // 2
		button_size = (400, 80)
		self.menu_buttons = [
			Button("Nowa gra", (button_x, button_y), button_size,
				   { "type": "mode_change", "mode": "start_game" }, font),
			Button("Autorzy", (button_x, button_y + 100), button_size,
				   { "type": "mode_change", "mode": "credits" }, font),
			Button("Twoja talia", (button_x, button_y + 200), button_size,
				   { "type": "mode_change", "mode": "deck" }, font),
			Button("Wyjście", (button_x, button_y + 300), button_size,
				   { "type": "mode_change", "mode": "exit" }, font)
		]

	@overrides
	def draw(self):
		super().draw()

		mouse_pos = pygame.mouse.get_pos()
		for btn in self.menu_buttons:
			btn.draw(self.screen, mouse_pos)

		self.volume_slider.draw(self.screen)

	@overrides
	def handle_events(self, event):
		if self.locked:
			return None

		self.volume_slider.handle_event(event)

		if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
			for btn in self.menu_buttons:
				if btn.check_click(event.pos):
					self.lock()
					return btn.action