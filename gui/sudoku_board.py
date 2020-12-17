import pygame

from gui.button import Button
import threading
import time
import numpy as np

from gui.layout import Layout


class SudokuBoard:

    def __init__(self):
        self.done = False

        self.cells_in_row = 9
        self.row_group_size = 3

        self.cells_in_column = 9
        self.column_group_size = 3

        self.groups_in_row = int(self.cells_in_row / self.row_group_size)
        self.groups_in_column = int(self.cells_in_column / self.column_group_size)

        pygame.font.init()
        self.font = pygame.font.SysFont("cambriacambriamath", 30)
        self.button_font = pygame.font.SysFont("cambriacambriamath", 18)
        self.info_font = pygame.font.SysFont("cambriacambriamath", 45, bold=True)

        self.cell_width = 40
        self.cell_height = 40
        self.margin = 10
        self.button_height = Button.check_size('', self.button_font)[1]

        self.grid_width = self.cell_width * self.cells_in_row + 2 * self.margin
        self.grid_height = self.cell_height * self.cells_in_column + 2 * self.margin
        self.window_width = self.grid_width
        self.window_height = self.grid_height + self.button_height + 1 * self.margin

        self.screen = pygame.display.set_mode((self.window_width, self.window_height))
        pygame.display.set_caption("Sudoku")

        self.line_color = (0, 0, 0)
        self.value_color = (0, 0, 0)
        self.info_color = (0, 0, 0)
        self.system_value_color = (44, 181, 2)
        self.highlight_color = (174, 237, 111)

        self.selected_row = 0
        self.selected_column = 0

        self.navigation_keys = {
            pygame.K_LEFT: (-1, 0),
            pygame.K_RIGHT: (1, 0),
            pygame.K_UP: (0, -1),
            pygame.K_DOWN: (0, 1),
        }

        self.grid = np.zeros(shape=(self.cells_in_row, self.cells_in_column), dtype=int)

        test_array = [[8, 3, 5, 4, 1, 6, 9, 2, 7],
                      [2, 9, 6, 8, 5, 7, 4, 3, 1],
                      [4, 1, 7, 2, 9, 3, 6, 5, 8],
                      [5, 6, 9, 1, 3, 4, 7, 8, 2],
                      [1, 2, 3, 6, 7, 8, 5, 4, 9],
                      [7, 4, 8, 5, 2, 9, 1, 6, 3],
                      [6, 5, 2, 7, 8, 1, 3, 9, 4],
                      [9, 8, 1, 3, 4, 5, 2, 7, 6],
                      [3, 7, 4, 9, 6, 2, 8, 1, 5]]
        test_array_unsolvable = [[7, 8, 1, 5, 4, 3, 9, 2, 6],
                                 [0, 0, 6, 1, 7, 9, 5, 0, 0],
                                 [9, 5, 4, 6, 2, 8, 7, 3, 1],
                                 [6, 9, 5, 8, 3, 7, 2, 1, 4],
                                 [1, 4, 8, 2, 6, 5, 3, 7, 9],
                                 [3, 2, 7, 9, 1, 4, 8, 0, 0],
                                 [4, 1, 3, 7, 5, 2, 6, 9, 8],
                                 [0, 0, 2, 0, 0, 0, 4, 0, 0],
                                 [5, 7, 9, 4, 8, 6, 1, 0, 3]]

        self.grid = np.array(test_array)
        self.elements_set = set([i for i in range(1, self.row_group_size * self.column_group_size + 1)])

        self.observers = []
        self.check_button = Button(parent=self,
                                   surface=self.screen,
                                   text="Check",
                                   font=self.button_font)
        self.check_button.set_on_click_event(self.check_and_display_info)
        self.solve_button = Button(parent=self,
                                   surface=self.screen,
                                   text="Solve",
                                   font=self.button_font)
        self.solve_button.set_on_click_event(lambda: threading.Thread(target=self.solve).start())

        self.buttons_layout = Layout(start=(self.margin, self.grid_height),
                                     max_size=self.window_width - 2 * self.margin)
        self.buttons_layout.add_element(self.check_button)
        self.buttons_layout.add_element(self.solve_button)

        self.info = None

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

    def draw_value(self, value, row, column):
        text = self.font.render(str(value), True, self.value_color)
        text_rect = text.get_rect(center=((column * self.cell_width) + self.margin + self.cell_width / 2,
                                          (row * self.cell_height) + self.margin + self.cell_height / 2,))
        self.screen.blit(text, text_rect)

    def draw_values(self):
        for i in range(self.cells_in_row):
            for j in range(self.cells_in_column):
                if self.grid[i][j] != 0:
                    self.draw_value(self.grid[i][j], i, j)

    def highlight_cell(self):
        if self.selected_row is None or self.selected_column is None:
            return
        line_fix_row = 2 if self.selected_row % self.row_group_size == 0 else 1
        line_fix_column = 2 if self.selected_column % self.column_group_size == 0 else 1
        pygame.draw.rect(surface=self.screen,
                         color=self.highlight_color,
                         rect=pygame.Rect(self.margin + self.selected_row * self.cell_width + line_fix_row,
                                          self.margin + self.selected_column * self.cell_height + line_fix_column,
                                          self.cell_width - line_fix_row,
                                          self.cell_height - line_fix_column)
                         )

    @staticmethod
    def check_limitations(new_value, minimum, maximum):
        if new_value > maximum:
            return False
        if new_value < minimum:
            return False
        return True

    def get_cell_pos(self, pos):
        cell_x = (pos[0] - self.margin) // (self.cell_width + 1)
        cell_y = (pos[1] - self.margin) // (self.cell_height + 1)
        return cell_x, cell_y

    def update_selected_cell(self, cell_x, cell_y):
        if SudokuBoard.check_limitations(cell_x, 0, self.cells_in_row - 1):
            if SudokuBoard.check_limitations(cell_y, 0, self.cells_in_column - 1):
                self.selected_row = cell_x
                self.selected_column = cell_y

    def check_mouse_navigation(self):
        self.update_selected_cell(*self.get_cell_pos(pygame.mouse.get_pos()))

    def check_keyboard_navigation(self, key):
        if key in self.navigation_keys.keys():
            self.update_selected_cell(self.selected_row + self.navigation_keys[key][0], self.selected_column + self.navigation_keys[key][1])
        elif key is pygame.K_BACKSPACE:
            self.grid[self.selected_column][self.selected_row] = 0
        else:
            s = pygame.key.name(key)
            s = s.replace('[', '')
            s = s.replace(']', '')
            if s.isdigit() and int(s) != 0:
                self.grid[self.selected_column][self.selected_row] = int(s)

    def draw_info(self):
        if self.info is None:
            return
        info = self.info_font.render(self.info, True, self.info_color)
        into_text_rect = info.get_rect(center=(self.grid_width / 2, self.grid_height / 2))
        self.screen.blit(info, into_text_rect)

    def draw(self):
        self.draw_lines(self.cells_in_row + 1, self.cell_width, False)
        self.draw_lines(self.cells_in_column + 1, self.cell_height, True)
        self.highlight_cell()
        self.draw_values()
        self.buttons_layout.draw()
        self.draw_info()

    def animate_and_hide_info(self):
        text = self.info
        for i in range(10):
            time.sleep(0.1)
            if i % 2 == 0:
                self.info = text
            else:
                self.info = None

    def display_info(self, message, positive=True):
        self.info = message
        self.info_color = (22, 112, 4) if positive else (186, 0, 0)
        threading.Thread(target=self.animate_and_hide_info).start()

    def check_and_display_info(self):
        correct = self.check()
        self.display_info("Correct" if correct else "Incorrect!", correct)

    def is_iterable_valid(self, iter_obj):
        return set(iter_obj) == self.elements_set

    def are_rows_valid(self, grid):
        return not any(not self.is_iterable_valid(row) for row in grid)

    def get_group(self, array, group_x_number, group_y_number):
        r_s = group_x_number * self.row_group_size
        c_s = group_y_number * self.column_group_size
        return array[r_s:r_s + self.row_group_size, c_s:c_s + self.column_group_size] \
            .reshape(self.row_group_size * self.column_group_size)

    def are_groups_valid(self):
        return not any(not self.is_iterable_valid(self.get_group(self.grid, i, j)) for i in range(self.groups_in_row)
                       for j in range(self.groups_in_column))

    def check(self):
        rows_correct = self.are_rows_valid(self.grid)
        columns_correct = self.are_rows_valid(np.rot90(self.grid))
        groups_correct = self.are_groups_valid()
        return rows_correct and columns_correct and groups_correct

    @staticmethod
    def remove_values_from_line(value, line):
        for i, element in enumerate(line):
            if value in element:
                element.remove(value)

    def remove_candidate_values(self, candidate_values, cell_x, cell_y):
        value = self.grid[cell_x][cell_y]

        self.remove_values_from_line(value, candidate_values[cell_x])
        self.remove_values_from_line(value, candidate_values[:, cell_y])
        group_x, group_y = cell_x // self.row_group_size, cell_y // self.column_group_size

        self.remove_values_from_line(value, self.get_group(candidate_values, group_x, group_y))

    def get_empty_cell(self, candidate_values):
        minimum = len(self.elements_set)
        x, y = -1, -1
        for i in range(self.cells_in_row):
            for j in range(self.cells_in_column):
                if self.grid[i][j] == 0 and len(candidate_values[i][j]) < minimum:
                    minimum = len(candidate_values[i][j])
                    x, y = i, j
                    if minimum == 1:
                        return x, y
        return x, y

    def solve(self):
        if not any(0 in row for row in self.grid):
            self.display_info('Solved!', positive=True)

        candidate_values = np.array([[self.elements_set.copy() if self.grid[i][j] == 0 else {self.grid[i][j]}
                                      for j in range(self.cells_in_row)] for i in range(self.cells_in_column)])

        for i in range(self.cells_in_row):
            for j in range(self.cells_in_column):
                if self.grid[i][j] != 0:
                    self.remove_candidate_values(candidate_values, i, j)

        while any(0 in row for row in self.grid):
            x, y = self.get_empty_cell(candidate_values)
            options = candidate_values[x][y]
            if len(options) == 1:
                self.grid[x][y] = options.pop()
            elif len(options) == 0:
                self.display_info('Unsolvable!', positive=False)
                return
            elif len(options) > 0:
                self.display_info('Not supported!', positive=False)
                return
            self.remove_candidate_values(candidate_values, x, y)
        self.display_info('Solved!', positive=True)

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
