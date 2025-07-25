import pygame

from src.view import loader as loader
from src.view.constants import ui_constants as u, deck_constants as c

class Scrollbar:
	def __init__(self, pos, height, color):
		self.pos = pos
		self.height = height
		self.path = u.SCROLL_PATH
		self.rect = pygame.Rect(pos, (c.SCROLLBAR_WIDTH, height))
		self.color = color

		self.offset = 0
		self.dragging = False
		self.scroll_start = None
		self.drag_start_y = None

	def draw(self, screen, content_length):
		if c.CARDS_PER_PAGE >= content_length:
			return

		proportion_visible = c.CARDS_PER_PAGE / content_length
		scroll_height = int(self.height * proportion_visible)
		max_scroll = content_length - c.CARDS_PER_PAGE
		y_offset = int((self.height - scroll_height) * self.offset / max_scroll)
		x_offset = (c.SCROLL_WIDTH - c.SCROLLBAR_WIDTH) // 2
		scrollbar_img = loader.load_image(self.path, (c.SCROLL_WIDTH, scroll_height))

		x, y = self.pos
		pygame.draw.rect(screen, self.color, self.rect)
		screen.blit(scrollbar_img, (x - x_offset, y + y_offset))

	def check_click(self, pos):
		return True if self.rect.collidepoint(pos) else False

	def update_offset(self, content_length, button):
		if button == 4:  # Scroll up
			self.offset = max(0, self.offset - c.COL_COUNT)
		elif button == 5:  # Scroll down
			max_scroll = max(0, content_length - c.CARDS_PER_PAGE)
			self.offset = min(max_scroll, self.offset + c.COL_COUNT)

	def update_drag_scroll(self, content_length, event_y):
		if not self.dragging:
			return

		max_scroll = max(0, content_length - c.CARDS_PER_PAGE)
		if max_scroll == 0:
			return

		delta_y = event_y - self.drag_start_y
		proportion_visible = c.CARDS_PER_PAGE / content_length
		scroll_height = int(self.height * proportion_visible)
		scroll_range = self.height - scroll_height
		scroll_delta = int(delta_y * max_scroll / scroll_range)
		new_offset = self.scroll_start + scroll_delta
		self.offset = max(0, min(max_scroll, new_offset))