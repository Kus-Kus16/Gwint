import pygame
from overrides import overrides

from src.presenter import loader as loader
from src.view.constants import ui_constants as u
from src.view.scenes.scene import Scene
from src.view.components.button import Button


class MenuScene(Scene):
	def __init__(self, screen):
		super().__init__(screen)

		button_width, button_height = u.BUTTON_SIZE_WIDE
		button_x = 184
		button_y = 387
		button_size = u.BUTTON_SIZE_WIDE
		button_paths = self.theme_buttons_paths
		self.buttons = [
			Button("Graj", (button_x, button_y), button_size,
				   self.button_newgame, image_paths=button_paths),
			Button("Twoja talia", (button_x, button_y + (button_height + 45)), button_size,
				   self.button_deck, image_paths=button_paths),
			Button("Ustawienia", (button_x, button_y + 2 * (button_height + 45)), button_size,
				   self.button_settings, image_paths=button_paths),
			Button("Autorzy", (button_x, button_y + 3 * (button_height + 45)), button_size,
				   self.button_credits, image_paths=button_paths),
			Button("Wyjście", (button_x, button_y + 4 * (button_height + 45)), button_size,
				   self.button_exit, image_paths=button_paths)
		]

	@overrides
	def draw(self):
		super().draw()

		overlay = pygame.Surface((500, self.screen_height), pygame.SRCALPHA)
		overlay.fill((0, 0, 0, 216))
		self.screen.blit(overlay, (134, 0))

		logo = loader.load_image(u.LOGO_PATH)
		self.screen.blit(logo, (192, 73))

		mouse_pos = pygame.mouse.get_pos()
		for btn in self.buttons:
			btn.draw(self.screen, mouse_pos)

		self.draw_temporary()

	@overrides
	def handle_events(self, event):
		if self.locked:
			return None

		if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
			for btn in self.buttons:
				if btn.check_click(event.pos):
					return btn.on_click()

	def change_mode(self, mode):
		self.lock()
		data = {"type": "mode_change", "mode": mode}
		return data

	def button_newgame(self):
		return self.change_mode("new_game")

	def button_deck(self):
		return self.change_mode("deck")

	def button_settings(self):
		return self.change_mode("settings")

	def button_credits(self):
		return self.change_mode("credits")

	def button_exit(self):
		return self.change_mode("exit")
