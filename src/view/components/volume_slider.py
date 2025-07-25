import pygame

from src.view.constants import ui_constants as u


# TODO deprecate
class VolumeSlider:
    def __init__(self, pos, size=(200, 20)):
        self.pos = pos
        self.size = size
        self.rect = pygame.Rect(pos, size)
        self.handle_radius = 15
        self.handle_x = pos[0] + size[0]//2
        self.dragging = False
        self.volume = 0.5

        self.bg_color = u.COLOR_BUTTON
        self.hover_color = u.COLOR_BUTTON_HOVER
        self.shadow_color = u.COLOR_GRAY
        self.handle_color = u.COLOR_WHITE

    def draw(self, screen):
        # Shadow
        shadow_rect = pygame.Rect(
            self.rect.x + 5,
            self.rect.y + 5,
            self.rect.width,
            self.rect.height
        )
        pygame.draw.rect(screen, self.shadow_color, shadow_rect, border_radius=20)

        # Background
        pygame.draw.rect(screen, self.bg_color, self.rect, border_radius=20)

        # Handle
        handle_center = (int(self.handle_x), self.rect.centery)
        pygame.draw.circle(screen, self.handle_color, handle_center, self.handle_radius)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self._is_over_handle(event.pos) or self.rect.collidepoint(event.pos):
                self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            x = max(self.rect.left, min(event.pos[0], self.rect.right))
            self.handle_x = x
            self.volume = (x - self.rect.left) / self.rect.width
            pygame.mixer.music.set_volume(self.volume)

            return True

        return False

    def _is_over_handle(self, pos):
        handle_center = (int(self.handle_x), self.rect.centery)
        return pygame.Vector2(pos).distance_to(handle_center) <= self.handle_radius
