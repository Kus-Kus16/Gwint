import pygame
from overrides import overrides

from view import constants as c, image_loader as loader
from view.scenes.scene import Scene
from view.components.button import Button


class MenuScene(Scene):
	def __init__(self, screen, volume_slider):
		super().__init__(screen, volume_slider=volume_slider)

		button_width, button_height = c.BUTTON_SIZE_WIDE
		button_x = 184
		button_y = 387
		button_size = c.BUTTON_SIZE_WIDE
		button_paths = c.THEME_BUTTON_PATHS
		self.menu_buttons = [
			Button("Nowa gra", (button_x, button_y), button_size,
				   { "type": "mode_change", "mode": "start_game" }, image_paths=button_paths),
			Button("Twoja talia", (button_x, button_y + (button_height + 45)), button_size,
				   {"type": "mode_change", "mode": "deck"}, image_paths=button_paths),
			Button("Ustawienia", (button_x, button_y + 2 * (button_height + 45)), button_size,
				   {"type": "mode_change", "mode": "settings"}, image_paths=button_paths),
			Button("Autorzy", (button_x, button_y + 3 * (button_height + 45)), button_size,
				   { "type": "mode_change", "mode": "credits" }, image_paths=button_paths),
			Button("Wyjście", (button_x, button_y + 4 * (button_height + 45)), button_size,
				   { "type": "mode_change", "mode": "exit" }, image_paths=button_paths)
		]

	@overrides
	def draw(self):
		super().draw()

		overlay = pygame.Surface((500, self.screen_height), pygame.SRCALPHA)
		overlay.fill((0, 0, 0, 216))
		self.screen.blit(overlay, (134, 0))

		logo = loader.load_image(c.LOGO_PATH)
		self.screen.blit(logo, (192, 73))

		mouse_pos = pygame.mouse.get_pos()
		for btn in self.menu_buttons:
			btn.draw(self.screen, mouse_pos)

		self.draw_temporary()
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