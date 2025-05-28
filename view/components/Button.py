import pygame

from view import Constants as C, ImageLoader


class Button:
	def __init__(self, text, pos, size, action=None, font=C.CINZEL_30_BOLD, image_paths=C.DEFAULT_BUTTON_PATHS):
		self.font = font
		self.text = text
		self.pos = pos
		self.size = size
		self.image_paths = image_paths
		self.images = ImageLoader.load_image(self.image_paths[0], self.size), ImageLoader.load_image(self.image_paths[1], self.size)
		self.action = action
		self.rect = pygame.Rect(pos, size)

		self.color = C.COLOR_BUTTON
		self.hover_color = C.COLOR_BUTTON_HOVER
		self.shadow_offset = 5

	def draw(self, screen, mouse_pos):
		image = self.images[0] if not self.rect.collidepoint(mouse_pos) else self.images[1]
		screen.blit(image, self.pos)

		label = self.font.render(self.text, True, C.COLOR_BLACK)
		screen.blit(label, (
			self.rect.centerx - label.get_width() // 2,
			self.rect.centery - label.get_height() // 2
		))

	def check_click(self, pos):
		return True if self.rect.collidepoint(pos) else False

