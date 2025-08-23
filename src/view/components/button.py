import pygame

from src.presenter.loader import Loader
from src.view.components.component import Component
from src.view.constants import ui_constants as u


class Button(Component):
	def __init__(self, screen, text, pos, size, on_click=None, font=None, image_paths=None):
		super().__init__(screen)
		self.font = font if font is not None else u.DEFAULT_FONT_BOLD
		self.text = text
		self.pos = pos
		self.size = size
		self.images = None
		self.never_update = image_paths is None
		self.load_images(image_paths)
		self.on_click = on_click
		self.rect = pygame.Rect(pos, size)

		self.color = u.COLOR_BUTTON
		self.hover_color = u.COLOR_BUTTON_HOVER
		self.shadow_offset = 5

	def draw(self, mouse_pos):
		image = self.images[0] if not self.rect.collidepoint(mouse_pos) else self.images[1]
		self.screen.blit(image, self.pos)
		self.draw_text(self.text, self.rect.centerx, self.rect.centery, color=u.COLOR_BLACK, font=self.font, center=True)

	def check_click(self, pos):
		return True if self.rect.collidepoint(pos) else False

	def load_images(self, image_paths):
		if self.never_update and self.images is not None:
			return

		image_paths = image_paths if image_paths is not None else u.DEFAULT_BUTTON_PATHS
		self.images = Loader.load_image(image_paths[0], self.size), Loader.load_image(image_paths[1], self.size)