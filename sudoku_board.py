import pygame


class SudokuBoard:

    def __init__(self):
        self.done = False

        self.x_cells = 9
        self.x_cells_group = 3

        self.y_cells = 9
        self.y_cells_group = 3

        self.cell_size_x = self.cell_size_y = 40
        self.margin = 10
        self.width = self.cell_size_x * self.x_cells + 2 * self.margin
        self.height = self.cell_size_y * self.y_cells + 2 * self.margin

        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Sudoku")

        self.line_color = (0, 0, 0)

    def quit(self):
        self.done = True

    def draw_lines(self, number_of_lines, step, horizontal):
        for i in range(number_of_lines):
            current_position = i * step + self.margin
            start = self.margin
            end = self.width if horizontal else self.height
            end -= self.margin

            start_pos = (start, current_position)
            end_pos = (end, current_position)

            if not horizontal:
                start_pos = start_pos[::-1]
                end_pos = end_pos[::-1]

            pygame.draw.line(surface=self.screen,
                             color=self.line_color,
                             start_pos=start_pos,
                             end_pos=end_pos,
                             width=(2 if i % 3 == 0 else 1))

    def draw(self):
        self.draw_lines(self.x_cells + 1, self.cell_size_x, False)
        self.draw_lines(self.y_cells + 1, self.cell_size_y, True)

    def start(self):
        while not self.done:
            self.screen.fill((255, 255, 255))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit()
            self.draw()
            pygame.display.update()
        pygame.quit()
