import pygame


class Button:

    DEFAULT_PADDING = 10

    def __init__(self, parent, surface, text, font, position, color=(200, 200, 200), text_color=(0, 0, 0),
                 cover_color=(150, 150, 150)):
        self.text = text
        self.text_color = text_color
        self.font = font

        self.surface = surface
        self.position = position
        self.padding = Button.DEFAULT_PADDING
        self.button_width = self.font.size(self.text)[0] + 2 * self.padding
        self.button_height = self.font.size(self.text)[1] + 2 * self.padding

        self.color = color
        self.cover_color = cover_color
        self.current_color = color

        parent.add_observer(self)

    @staticmethod
    def get_size(text, font, padding=DEFAULT_PADDING):
        return [dim + 2 * padding for dim in font.size(text)]

    def draw(self):
        pygame.draw.rect(self.surface, self.current_color,
                         pygame.Rect(self.position, (self.button_width, self.button_height)))
        text = self.font.render(self.text, True, self.text_color)
        text_rect = text.get_rect(center=(self.position[0] + self.button_width / 2,
                                          self.position[1] + self.button_height / 2))
        self.surface.blit(text, text_rect)

    def is_mouse_over(self, mouse_position):
        if 0 < mouse_position[0] - self.position[0] < self.button_width:
            if 0 < mouse_position[1] - self.position[1] < self.button_height:
                return True
        return False

    def process_event(self, event, mouse_position):
        if self.is_mouse_over(mouse_position):
            self.current_color = self.cover_color
        else:
            self.current_color = self.color
