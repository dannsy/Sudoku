"""This module contains SudokuGame class.
Starts the Sudoku game.
"""
import os
import random

import numpy as np
import pygame

from sudoku_gui import SudokuGui
from sudoku_generator import main

# color definitions
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
LIGHT_BLUE = (170, 170, 230)
WHITE_BLUE = (200, 200, 235)
# dimensions of display
WIDTH = 450
HEIGHT = 505


class SudokuGame:
    """Creates the main menu launches game depending on player choice
    """

    def __init__(self):
        self.width = WIDTH
        self.height = HEIGHT
        self.display = pygame.display.set_mode((self.width, self.height))
        self.running = True
        self.play_pressed = False
        self.but0_height = 340
        self.but1_height = 400
        self.image_top = 100
        self.image_left = 135
        self.spacing = 60
        self.generated_board = None
        self.start_main()

    def choose_board(self, difficulty):
        """Choose a random board from generated boards
        """
        try:
            difficulty_dir = os.path.join(os.getcwd(), "boards", difficulty)
            board_list = os.listdir(difficulty_dir)
            chosen = random.choice(board_list)
            print(chosen)
            self.generated_board = np.load(os.path.join(difficulty_dir, chosen))
            os.remove(os.path.join(difficulty_dir, chosen))
            if len(board_list) <= 1:
                main(5, difficulty)
        except FileNotFoundError:
            main(5, difficulty)
            difficulty_dir = os.path.join(os.getcwd(), "boards", difficulty)
            board_list = os.listdir(difficulty_dir)
            chosen = random.choice(board_list)
            print(chosen)
            self.generated_board = np.load(os.path.join(difficulty_dir, chosen))
            os.remove(os.path.join(difficulty_dir, chosen))

    def select_button(self, pos):
        """Get selected button from mouse position and activate it

        Args:
            pos (tup of 2 ints): pos[0] is the x-position of mouse,
                pos[1] is the y-position of mouse
        """
        if pos[0] > 170 and pos[0] < 280:
            if pos[1] > self.but0_height and pos[1] < self.but0_height + 45:
                self.play_pressed = True
            elif pos[1] > self.but1_height and pos[1] < self.but1_height + 45:
                sudoku_game = SudokuGui(np.zeros((9, 9), dtype=int), fill_own=True)
                sudoku_game.start_game()

        elif self.play_pressed and pos[0] > 300 and pos[0] < 370:
            if pos[1] > self.but0_height - 20 and pos[1] < self.but0_height + 5:
                self.choose_board("easy")
                sudoku_game = SudokuGui(self.generated_board)
                sudoku_game.start_game()
                self.play_pressed = False
            elif pos[1] > self.but0_height + 10 and pos[1] < self.but0_height + 35:
                self.choose_board("medium")
                sudoku_game = SudokuGui(self.generated_board)
                sudoku_game.start_game()
                self.play_pressed = False
            elif pos[1] > self.but0_height + 40 and pos[1] < self.but0_height + 65:
                self.choose_board("hard")
                sudoku_game = SudokuGui(self.generated_board)
                sudoku_game.start_game()
                self.play_pressed = False

        else:
            self.play_pressed = False

    def image_cell(self, num, img_x, img_y):
        """Finds and places the Sudoku numbers at the right place on the menu.

        Args:
            num (int): The number to display
            img_x (int): the x coordinate of the corner of the cell
            img_y (int): the y coordinate of the corner of the cell
        """
        font = pygame.font.SysFont("arial", 30)
        text = font.render(str(num), True, BLACK)
        self.display.blit(
            text, (img_x - text.get_width() / 2, img_y - text.get_height() / 2),
        )

    def menu_gui(self):
        """Initialize main menu GUI
        """
        self.display.fill(WHITE)

        # drawing lines
        pygame.draw.line(
            self.display,
            BLACK,
            (self.image_left, self.image_top + self.spacing),
            (self.width - 135, self.image_top + self.spacing),
            2,
        )
        pygame.draw.line(
            self.display,
            BLACK,
            (self.image_left, self.image_top + self.spacing * 2),
            (self.image_left + self.spacing * 3, self.image_top + self.spacing * 2),
            2,
        )
        pygame.draw.line(
            self.display,
            BLACK,
            (self.image_left + self.spacing, self.image_top),
            (self.image_left + self.spacing, self.image_top + self.spacing * 3),
            2,
        )
        pygame.draw.line(
            self.display,
            BLACK,
            (self.image_left + self.spacing * 2, self.image_top),
            (self.image_left + self.spacing * 2, self.image_top + self.spacing * 3),
            2,
        )

        # drawing 1, 3, 5, 7, 9
        self.image_cell(
            1, self.image_left + self.spacing / 2, self.image_top + self.spacing / 2
        )
        self.image_cell(
            3, self.image_left + self.spacing * 2.5, self.image_top + self.spacing / 2
        )
        self.image_cell(
            5, self.image_left + self.spacing * 1.5, self.image_top + self.spacing * 1.5
        )
        self.image_cell(
            7, self.image_left + self.spacing / 2, self.image_top + self.spacing * 2.5
        )
        self.image_cell(
            9, self.image_left + self.spacing * 2.5, self.image_top + self.spacing * 2.5
        )

        # drawing button and logo
        if self.play_pressed:
            self.display.fill(WHITE_BLUE, pygame.Rect(170, self.but0_height, 110, 45))
            self.display.fill(
                LIGHT_BLUE, pygame.Rect(300, self.but0_height - 20, 70, 25)
            )
            self.display.fill(
                LIGHT_BLUE, pygame.Rect(300, self.but0_height + 10, 70, 25)
            )
            self.display.fill(
                LIGHT_BLUE, pygame.Rect(300, self.but0_height + 40, 70, 25)
            )
            font = pygame.font.SysFont("arial", 18)
            text = font.render("EASY", True, BLACK)
            self.display.blit(text, (305, self.but0_height - 18))
            text = font.render("MEDIUM", True, BLACK)
            self.display.blit(text, (305, self.but0_height + 12))
            text = font.render("HARD", True, BLACK)
            self.display.blit(text, (305, self.but0_height + 42))
        else:
            self.display.fill(LIGHT_BLUE, pygame.Rect(170, self.but0_height, 110, 45))
        self.display.fill(LIGHT_BLUE, pygame.Rect(170, self.but1_height, 110, 45))

        font = pygame.font.SysFont("arial", 40)
        text = font.render("SUDOKU", True, BLACK)
        self.display.blit(text, (155, 30))

        font = pygame.font.SysFont("arial", 30)
        text = font.render("PLAY", True, BLACK)
        self.display.blit(text, (192, self.but0_height + 4))

        font = pygame.font.SysFont("arial", 30)
        text = font.render("INPUT", True, BLACK)
        self.display.blit(text, (187, self.but1_height + 4))

    def start_main(self):
        """Starts the main menu
        """
        self.menu_gui()
        pygame.display.set_caption("Sudoku")
        # main loop of main menu
        while self.running:
            for event in pygame.event.get():
                # enable closing of display
                if event.type == pygame.QUIT:
                    self.running = False
                    return
                # getting position of mouse
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    self.select_button(mouse_pos)
                # # getting keyboard input
                # if event.type == pygame.KEYDOWN:
                #     keys = pygame.key.get_pressed()

            self.menu_gui()
            pygame.display.update()


def main_game():
    """Launches the Sudoku GUI with a random board.
    Creates new boards when no more boards available
    """
    pygame.init()
    SudokuGame()
    pygame.quit()


if __name__ == "__main__":
    main_game()
