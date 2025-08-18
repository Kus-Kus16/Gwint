import pygame
from src.view.constants import ui_constants as u
from src.presenter import settings


class VolumeSlider:
    def __init__(self, pos, size=(200, 20)):
        self.pos = pos
        self.size = size
        self.rect = pygame.Rect(pos, size)
        self.handle_radius = 15
        self.dragging = False

        self.volume = settings.load_setting("volume")

        self.bg_color = u.COLOR_GRAY
        self.hover_color = u.COLOR_LIGHTGRAY
        self.shadow_color = u.COLOR_BLACK
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

        handle_x = self.rect.left + self.volume * self.rect.width
        handle_center = (int(handle_x), self.rect.centery)
        pygame.draw.circle(screen, self.handle_color, handle_center, self.handle_radius)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self._is_over_handle(event.pos) or self.rect.collidepoint(event.pos):
                self.dragging = True

        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False

        elif event.type == pygame.MOUSEMOTION and self.dragging:
            x = max(self.rect.left, min(event.pos[0], self.rect.right))
            self.volume = (x - self.rect.left) / self.rect.width
            settings.save_setting("volume", self.volume)
            pygame.mixer.music.set_volume(self.volume)
            return True

        return False

    def _is_over_handle(self, pos):
        handle_x = self.rect.left + self.volume * self.rect.width
        handle_center = (int(handle_x), self.rect.centery)
        return pygame.Vector2(pos).distance_to(handle_center) <= self.handle_radius
