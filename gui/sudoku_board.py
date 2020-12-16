import pygame

from gui.button import Button


class SudokuBoard:

    def __init__(self):
        self.done = False

        self.x_cells = 9
        self.x_cells_group = 3

        self.y_cells = 9
        self.y_cells_group = 3

        pygame.font.init()
        self.font = pygame.font.SysFont("cambriacambriamath", 30)
        self.button_font = pygame.font.SysFont("cambriacambriamath", 18)

        self.cell_size_x = self.cell_size_y = 40
        self.margin = 10
        self.button_height = Button.get_size('', self.button_font)[1]

        self.grid_width = self.cell_size_x * self.x_cells + 2 * self.margin
        self.grid_height = self.cell_size_y * self.y_cells + 2 * self.margin
        self.window_width = self.grid_width
        self.window_height = self.grid_height + self.button_height + 1 * self.margin

        self.screen = pygame.display.set_mode((self.window_width, self.window_height))
        pygame.display.set_caption("Sudoku")

        self.line_color = (0, 0, 0)
        self.value_color = (0, 0, 0)
        self.system_value_color = (44, 181, 2)
        self.highlight_color = (174, 237, 111)

        self.x = 0
        self.y = 0

        self.navigation_keys = {
            pygame.K_LEFT: (-1, 0),
            pygame.K_RIGHT: (1, 0),
            pygame.K_UP: (0, -1),
            pygame.K_DOWN: (0, 1),
        }

        self.grid = [[0 for _ in range(self.x_cells)] for _ in range(self.y_cells)]

        self.observers = []
        self.check_button = Button(parent=self,
                                   surface=self.screen,
                                   text="Check",
                                   font=self.button_font,
                                   position=(self.margin, self.grid_height))

    def add_observer(self, observer):
        self.observers.append(observer)

    def quit(self):
        self.done = True

    def draw_lines(self, number_of_lines, step, horizontal):
        for i in range(number_of_lines):
            current_position = i * step + self.margin
            start = self.margin
            end = self.grid_width if horizontal else self.grid_height
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

    def draw_value(self, value, x, y):
        text = self.font.render(str(value), True, self.value_color)
        text_rect = text.get_rect(center=((x * self.cell_size_x) + self.margin + self.cell_size_x / 2,
                                          (y * self.cell_size_y) + self.margin + self.cell_size_y / 2))
        self.screen.blit(text, text_rect)

    def draw_values(self):
        for i in range(self.x_cells):
            for j in range(self.y_cells):
                if self.grid[i][j] != 0:
                    self.draw_value(self.grid[i][j], i, j)

    def highlight_cell(self):
        if self.x is None or self.y is None:
            return
        line_fix_x = 2 if self.x % self.x_cells_group == 0 else 1
        line_fix_y = 2 if self.y % self.y_cells_group == 0 else 1
        pygame.draw.rect(surface=self.screen,
                         color=self.highlight_color,
                         rect=pygame.Rect(self.margin + self.x * self.cell_size_x + line_fix_x,
                                          self.margin + self.y * self.cell_size_y + line_fix_y,
                                          self.cell_size_x - line_fix_x,
                                          self.cell_size_y - line_fix_y)
                         )

    @staticmethod
    def check_limitations(new_value, minimum, maximum):
        if new_value > maximum:
            return False
        if new_value < minimum:
            return False
        return True

    def get_cell_pos(self, pos):
        cell_x = (pos[0] - self.margin) // (self.cell_size_x + 1)
        cell_y = (pos[1] - self.margin) // (self.cell_size_y + 1)
        return cell_x, cell_y

    def update_selected_cell(self, cell_x, cell_y):
        if SudokuBoard.check_limitations(cell_x, 0, self.x_cells - 1):
            if SudokuBoard.check_limitations(cell_y, 0, self.y_cells - 1):
                self.x = cell_x
                self.y = cell_y

    def check_mouse_navigation(self):
        self.update_selected_cell(*self.get_cell_pos(pygame.mouse.get_pos()))

    def check_keyboard_navigation(self, key):
        if key in self.navigation_keys.keys():
            self.update_selected_cell(self.x + self.navigation_keys[key][0], self.y + self.navigation_keys[key][1])
        elif key is pygame.K_BACKSPACE:
            self.grid[self.x][self.y] = 0
        else:
            s = pygame.key.name(key)
            s = s.replace('[', '')
            s = s.replace(']', '')
            if s.isdigit() and int(s) != 0:
                self.grid[self.x][self.y] = int(s)

    def draw(self):
        self.draw_lines(self.x_cells + 1, self.cell_size_x, False)
        self.draw_lines(self.y_cells + 1, self.cell_size_y, True)
        self.highlight_cell()
        self.draw_values()
        self.check_button.draw()

    def start(self):
        while not self.done:
            self.screen.fill((255, 255, 255))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit()
                if event.type == pygame.KEYDOWN:
                    self.check_keyboard_navigation(event.key)
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.check_mouse_navigation()
                for observer in self.observers:
                    observer.process_event(event, pygame.mouse.get_pos())
            self.draw()
            pygame.display.update()
        pygame.quit()
