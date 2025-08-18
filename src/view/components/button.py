import pygame

from src.view import loader as loader
from src.view.constants import ui_constants as u


class Button:
	def __init__(self, text, pos, size, on_click=None, font=None, image_paths=None):
		self.font = font if font is not None else u.DEFAULT_FONT_BOLD
		self.text = text
		self.pos = pos
		self.size = size
		self.image_paths = image_paths if image_paths is not None else u.DEFAULT_BUTTON_PATHS
		self.images = loader.load_image(self.image_paths[0], self.size), loader.load_image(self.image_paths[1], self.size)
		self.on_click = on_click
		self.rect = pygame.Rect(pos, size)

		self.color = u.COLOR_BUTTON
		self.hover_color = u.COLOR_BUTTON_HOVER
		self.shadow_offset = 5

	def draw(self, screen, mouse_pos):
		image = self.images[0] if not self.rect.collidepoint(mouse_pos) else self.images[1]
		screen.blit(image, self.pos)

		label = self.font.render(self.text, True, u.COLOR_BLACK)
		screen.blit(label, (
			self.rect.centerx - label.get_width() // 2,
			self.rect.centery - label.get_height() // 2
		))

	def check_click(self, pos):
		return True if self.rect.collidepoint(pos) else False

