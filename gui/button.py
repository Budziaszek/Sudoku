import pygame


class Button:

    DEFAULT_PADDING = 10

    def __init__(self, parent, surface, text, font, position, color=(200, 200, 200), text_color=(0, 0, 0),
                 cover_color=(300, 300, 300)):
        self.surface = surface
        self.text = text
        self.position = position
        self.color = color
        self.cover_color = cover_color
        self.text_color = text_color
        self.current_color = color
        self.font = font
        self.padding = Button.DEFAULT_PADDING
        parent.add_observer(self)
        self.button_width = self.font.size(self.text)[0] + 2 * self.padding
        self.button_height = self.font.size(self.text)[1] + 2 * self.padding

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

    def process_event(self, event, mouse_position):
        pass