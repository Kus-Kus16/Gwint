
from src.view.components.button import Button
from src.view.components.component import Component
from src.view.constants import ui_constants as u

class Setting(Component):
    def __init__(self, screen, title, pos, options, on_change, initial_index, can_wrap=True):
        super().__init__(screen)
        self.font = u.CINZEL_25
        self.title_font = u.CINZEL_30_BOLD
        self.title = title
        self.pos = pos
        self.options = options
        self.on_change = on_change
        self.index = initial_index
        self.can_wrap = can_wrap

        x, y = self.pos
        self.arrows = [
            Button(self.screen, "", (x - 250 - u.ARROW_SIZE[0], y + 80), u.ARROW_SIZE,
                   self.button_left, image_paths=u.DEFAULT_LEFT_ARROW_PATHS),
            Button(self.screen,"", (x + 250, y + 80), u.ARROW_SIZE,
                   self.button_right, image_paths=u.DEFAULT_RIGHT_ARROW_PATHS)
        ]

    def draw(self, mouse_pos):
        x, y = self.pos

        self.draw_text(self.title, x, y + 50, font=self.title_font, center=True)
        self.draw_text(self.options[self.index], x, y + 121, font=self.font, center=True)

        for arrow in self.arrows:
            arrow.draw(mouse_pos)

    def handle_events(self, event):
        for arrow in self.arrows:
            if arrow.check_click(event.pos):
                arrow.on_click()
                return True

        return False

    def button_left(self):
        self.change_option(-1)

    def button_right(self):
        self.change_option(+1)

    def change_option(self, direction):
        if self.can_wrap:
            index = (self.index + direction) % len(self.options)
        else:
            index = max(0, min(self.index + direction, len(self.options) - 1))

        if index == self.index:
            return

        self.index = index
        self.on_change(self.index)