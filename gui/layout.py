import pygame


class Layout:

    DEFAULT_PADDING = 10
    HORIZONTAL = 0
    VERTICAL = 1

    def __init__(self, start, max_size, orientation=HORIZONTAL, padding=DEFAULT_PADDING):
        self.start = start
        self.max_size = max_size
        self.padding = padding
        self.elements = list()
        self.current_size = [0, 0]
        self.orientation = orientation

    def add_element(self, element):
        self.elements.append(element)
        move_hor, move_ver = self.current_size
        if self.orientation == Layout.HORIZONTAL:
            move_ver = 0
        else:
            move_hor = 0
        element.position = (self.start[0] + move_hor, self.start[1] + move_ver)
        self.current_size[0] += element.get_size()[0] + self.padding
        self.current_size[1] += element.get_size()[1] + self.padding

    def draw(self):
        for element in self.elements:
            element.draw()

