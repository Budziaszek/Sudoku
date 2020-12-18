from collections import Counter
from random import randrange, choice, shuffle

import pygame

from gui.button import Button
import threading
import time
import numpy as np

from gui.layout import Layout


class SudokuBoard:
    INPUT = 0
    ACCEPTED = 1
    WRONG = -1

    def __init__(self):
        self.done = False
        self.remove_attempts = 5

        self.cells_in_row = 9
        self.row_group_size = 3

        self.cells_in_column = 9
        self.column_group_size = 3

        self.groups_in_row = int(self.cells_in_row / self.row_group_size)
        self.groups_in_column = int(self.cells_in_column / self.column_group_size)

        pygame.font.init()
        self.font = pygame.font.SysFont("cambriacambriamath", 30)
        self.button_font = pygame.font.SysFont("cambriacambriamath", 19)
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
        self.input_value_color = (0, 0, 0)
        self.accepted_value_color = (44, 181, 2)
        self.wrong_value_color = (181, 20, 20)
        self.info_color = (0, 0, 0)
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
        self.grid_status = np.full(shape=(self.cells_in_row, self.cells_in_column), fill_value=SudokuBoard.ACCEPTED)

        self.elements_set = set([i for i in range(1, self.row_group_size * self.column_group_size + 1)])

        self.observers = []
        self.puzzle_button = Button(parent=self, surface=self.screen, text="New puzzle", font=self.button_font)
        self.puzzle_button.set_on_click_event(lambda: threading.Thread(target=self.generate_puzzle).start())
        self.hint_button = Button(parent=self, surface=self.screen, text="Hint", font=self.button_font)
        self.hint_button.set_on_click_event(lambda: threading.Thread(target=self.hint).start())
        self.check_button = Button(parent=self, surface=self.screen, text="Check", font=self.button_font)
        self.check_button.set_on_click_event(self.check_and_display_info)
        self.solve_button = Button(parent=self, surface=self.screen, text="Solve", font=self.button_font)
        self.solve_button.set_on_click_event(lambda: threading.Thread(target=self.solve).start())
        self.clean_button = Button(parent=self, surface=self.screen, text="Clean", font=self.button_font)
        self.clean_button.set_on_click_event(lambda: threading.Thread(target=self.clean).start())

        self.buttons_layout = Layout(start=(self.margin, self.grid_height),
                                     max_size=self.window_width - 2 * self.margin)
        self.buttons_layout.add_element(self.puzzle_button)
        self.buttons_layout.add_element(self.hint_button)
        self.buttons_layout.add_element(self.check_button)
        self.buttons_layout.add_element(self.solve_button)
        self.buttons_layout.add_element(self.clean_button)

        self.info = None

    def clean(self):
        self.grid = np.zeros(shape=(self.cells_in_row, self.cells_in_column), dtype=int)
        self.grid_status = np.full(shape=(self.cells_in_row, self.cells_in_column), fill_value=SudokuBoard.ACCEPTED)

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
        color = self.input_value_color
        if self.grid_status[row][column] == SudokuBoard.WRONG:
            color = self.wrong_value_color
        if self.grid_status[row][column] == SudokuBoard.ACCEPTED:
            color = self.accepted_value_color
        text = self.font.render(str(value), True, color)
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
            self.update_selected_cell(self.selected_row + self.navigation_keys[key][0],
                                      self.selected_column + self.navigation_keys[key][1])
        elif key is pygame.K_BACKSPACE:
            self.grid[self.selected_column][self.selected_row] = 0
            self.grid_status[self.selected_column][self.selected_row] = SudokuBoard.INPUT
        else:
            s = pygame.key.name(key)
            s = s.replace('[', '')
            s = s.replace(']', '')
            if s.isdigit() and int(s) != 0:
                self.grid[self.selected_column][self.selected_row] = int(s)
                self.grid_status[self.selected_column][self.selected_row] = SudokuBoard.INPUT

    def draw_info(self):
        if self.info is None:
            return
        info_text = self.info.split('\n')
        for i, text in enumerate(info_text):
            info = self.info_font.render(text, True, self.info_color)
            into_text_rect = info.get_rect(center=(self.grid_width / 2, self.grid_height / 2
                                                   + info.get_size()[1] * i - info.get_size()[1] * len(info_text) / 2))
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

    @staticmethod
    def get_wrong(line):
        c = Counter(line)
        for key in c:
            if c[key] > 1:
                for i, cell in enumerate(line):
                    if cell == key:
                        yield i

    def hint(self):
        for i, row in enumerate(self.grid):
            for j in SudokuBoard.get_wrong(row):
                if self.grid_status[i][j] != SudokuBoard.ACCEPTED:
                    self.grid_status[i][j] = SudokuBoard.WRONG
        for j in range(self.cells_in_column):
            column = self.grid[:, j]
            for i in SudokuBoard.get_wrong(column):
                if self.grid_status[i][j] != SudokuBoard.ACCEPTED:
                    self.grid_status[i][j] = SudokuBoard.WRONG

    def check(self):
        rows_correct = self.are_rows_valid(self.grid)
        columns_correct = self.are_rows_valid(np.rot90(self.grid))
        groups_correct = self.are_groups_valid()
        return rows_correct and columns_correct and groups_correct

    @staticmethod
    def modify_values_in_line(value, line, modify_function):
        for i, element in enumerate(line):
            if value in element:
                modify_function(element, value)
                # element.remove(value)

    def modify_candidate_values(self, grid, candidate_values, cell_x, cell_y, modify_function):
        value = grid[cell_x][cell_y]

        self.modify_values_in_line(value, candidate_values[cell_x], modify_function)
        self.modify_values_in_line(value, candidate_values[:, cell_y], modify_function)

        group_x, group_y = cell_x // self.row_group_size, cell_y // self.column_group_size
        self.modify_values_in_line(value, self.get_group(candidate_values, group_x, group_y), modify_function)

    def get_empty_cell(self, grid, candidate_values):
        minimum = len(self.elements_set)
        x, y = -1, -1
        for i in range(self.cells_in_row):
            for j in range(self.cells_in_column):
                if grid[i][j] == 0 and len(candidate_values[i][j]) < minimum:
                    minimum = len(candidate_values[i][j])
                    x, y = i, j
                    if minimum == 1:
                        return x, y
        return x, y

    def prepare_run(self, values, candidate_values, option, x, y):
        # v = values.copy()
        # c_v = candidate_values.copy()
        values[x][y] = option
        self.modify_candidate_values(values, candidate_values, x, y, lambda s, v: s.remove(v))
        return self.run_solver(values, self.prepare_candidate_values(values))

    def run_solver(self, values, candidate_values):
        # Solved
        if not any(0 in row for row in values):
            yield values
        # Choose empty cell with fewest candidate values
        x, y = self.get_empty_cell(values, candidate_values)
        options = candidate_values[x][y]
        # Unsolvable
        if len(options) == 0:
            yield None
        else:
            options_list = list(options)
            shuffle(options_list)
            for option in options_list:
                values[x][y] = option
                self.modify_candidate_values(values, candidate_values, x, y, lambda s, v: s.remove(v))
                yield from self.run_solver(values, self.prepare_candidate_values(values))
                values[x][y] = 0
                self.modify_candidate_values(values, candidate_values, x, y, lambda s, v: s.add(v))

    def prepare_candidate_values(self, grid):
        candidate_values = np.array([[self.elements_set.copy() if grid[i][j] == 0 else {grid[i][j]}
                                      for j in range(self.cells_in_row)] for i in range(self.cells_in_column)])

        for i in range(self.cells_in_row):
            for j in range(self.cells_in_column):
                if grid[i][j] != 0:
                    self.modify_candidate_values(grid, candidate_values, i, j, lambda s, v: s.remove(v))
        return candidate_values

    def solve(self):
        if not any(0 in row for row in self.grid):
            self.display_info('Solved!', positive=True)
            return

        if np.count_nonzero(self.grid == 0) == self.cells_in_row * self.cells_in_column:
            self.display_info('Enter values!', positive=False)
            return

        grid = self.grid.copy()
        counter = 0
        solution = None
        for result in self.run_solver(grid, self.prepare_candidate_values(grid)):
            if counter > 1:
                self.display_info('Not uniquely\n solvable!', positive=False)
                return
            if result is not None:
                counter += 1
                solution = result.copy()
        if solution is not None:
            self.display_info('Solved!', positive=True)
            self.grid = solution
            return
        self.display_info('Unsolvable!', positive=False)

    def generate_grid(self):
        self.clean()
        grid = self.grid.copy()
        candidate_values = self.prepare_candidate_values(grid)
        for _ in range(10):
            row_random, column_random = randrange(0, self.cells_in_row, 1), randrange(0, self.cells_in_column, 1)
            grid[row_random][column_random] = choice(list(candidate_values[row_random][column_random]))
            self.modify_candidate_values(grid, candidate_values, row_random, column_random, lambda s, v: s.remove(v))

        for result in self.run_solver(grid, self.prepare_candidate_values(grid)):
            if result is not None:
                return result.copy()

    def generate_puzzle(self):
        grid = self.generate_grid()

        remove = 0
        while remove < self.remove_attempts:
            row_random, column_random = randrange(0, self.cells_in_row, 1), randrange(0, self.cells_in_column, 1)
            if grid[row_random][column_random] == 0:
                continue
            value = grid[row_random][column_random]
            grid[row_random][column_random] = 0
            counter = 0
            for result in self.run_solver(grid.copy(), self.prepare_candidate_values(grid)):
                if result is not None:
                    counter += 1
                if counter > 1:
                    remove += 1
                    grid[row_random][column_random] = value
                    break
        self.grid = grid

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
