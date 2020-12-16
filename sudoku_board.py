import pygame


class SudokuBoard:

    def __init__(self):
        self.done = False

        width, height = 600, 600
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Sudoku")

    def quit(self):
        self.done = True

    def start(self):
        while not self.done:
            self.screen.fill((255, 255, 255))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit()
            pygame.display.update()
        pygame.quit()
