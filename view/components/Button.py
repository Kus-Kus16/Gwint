import pygame


class Button:
	def __init__(self, text, pos, size, action=None, font=None):
		self.font = font if font else pygame.font.SysFont(None, 40)
		self.text = text
		self.pos = pos
		self.size = size
		self.action = action
		self.rect = pygame.Rect(pos, size)

		self.color = (139, 69, 19)
		self.hover_color = (160, 82, 45)
		self.shadow_offset = 5

	def draw(self, screen):
		# Cień
		shadow_rect = pygame.Rect(self.rect.x + self.shadow_offset, self.rect.y + self.shadow_offset, self.rect.width, self.rect.height)

		pygame.draw.rect(screen, (50, 50, 50), shadow_rect, border_radius=20)

		pygame.draw.rect(screen, self.color, self.rect, border_radius=20)

		label = self.font.render(self.text, True, (255, 255, 255))
		screen.blit(label, (
			self.rect.centerx - label.get_width() // 2,
			self.rect.centery - label.get_height() // 2
		))

	def check_click(self, pos):
		if self.rect.collidepoint(pos):
			if self.action:
				self.action()

	def on_hover(self, pos):
		if self.rect.collidepoint(pos):
			self.color = self.hover_color
		else:
			self.color = (139, 69, 19)

