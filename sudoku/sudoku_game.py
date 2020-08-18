"""This module contains SudokuGame class.
Starts the Sudoku game.
"""
import multiprocessing
import os
import random
import sys

import numpy as np
import pygame

from sudoku import BOARD_LOC
from sudoku.utils.sudoku_generator import main
from sudoku.utils.sudoku_gui import SudokuGui

# color definitions
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
LIGHT_BLUE = (170, 170, 230)
WHITE_BLUE = (200, 200, 235)
# dimensions of display
WIDTH = 540
HEIGHT = 660

FPS_FLAG = False


class SudokuGame:
    """Creates the main menu launches game depending on player choice
    """

    width = WIDTH
    height = HEIGHT
    display = None

    bb_xpos = int(width / 3)
    bb0_ypos = int(height * 0.7)
    bb1_ypos = int(height * 0.8)
    bb_height = int(height * 0.1 - 6)
    bb_width = int(width / 3)

    sb_xpos = int(width / 3 * 2 + 10)
    sb_width = int(bb_width * 0.6)
    sb_height = int(bb_height * 0.6)
    height_diff = (bb_height - sb_height) // 2

    i_top = int(height * 0.2)
    i_left = int(width * 0.25)
    spacing = int(width * 0.5 / 3)

    play_but = pygame.Rect(bb_xpos, bb0_ypos, bb_width, bb_height)
    input_but = pygame.Rect(bb_xpos, bb1_ypos, bb_width, bb_height)
    easy_but = pygame.Rect(sb_xpos, bb0_ypos - sb_height, sb_width, sb_height)
    med_but = pygame.Rect(sb_xpos, bb0_ypos + height_diff, sb_width, sb_height)
    hard_but = pygame.Rect(sb_xpos, bb0_ypos + bb_height, sb_width, sb_height)

    def __init__(self):
        self.running = True
        self.play_pressed = False
        self.generated_board = None
        self.start_main()

    def choose_board(self, difficulty):
        """Choose a random board from generated boards
        """
        try:
            difficulty_dir = os.path.join(BOARD_LOC, difficulty)
            board_list = os.listdir(difficulty_dir)
            chosen = random.choice(board_list)
            print(chosen)
            self.generated_board = np.load(os.path.join(difficulty_dir, chosen))
            os.remove(os.path.join(difficulty_dir, chosen))
            if len(board_list) <= 1:
                pro1 = multiprocessing.Process(target=main, args=[10, difficulty])
                pro1.start()
        except (FileNotFoundError, IndexError):
            main(2, difficulty)
            difficulty_dir = os.path.join(BOARD_LOC, difficulty)
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
        # PLAY
        if self.play_but.collidepoint(pos):
            self.play_pressed = True
        # INPUT
        elif self.input_but.collidepoint(pos):
            sudoku_game = SudokuGui(np.zeros((9, 9), dtype=int), fill_own=True)
            sudoku_game.start_game()
        # EASY
        elif self.easy_but.collidepoint(pos):
            self.choose_board("easy")
            sudoku_game = SudokuGui(self.generated_board)
            sudoku_game.start_game()
            self.play_pressed = False
        # MEDIUM
        elif self.med_but.collidepoint(pos):
            self.choose_board("medium")
            sudoku_game = SudokuGui(self.generated_board)
            sudoku_game.start_game()
            self.play_pressed = False
        # HARD
        elif self.hard_but.collidepoint(pos):
            self.choose_board("hard")
            sudoku_game = SudokuGui(self.generated_board)
            sudoku_game.start_game()
            self.play_pressed = False
        else:
            self.play_pressed = False

    def i_cell(self, num, img_x, img_y):
        """Finds and places the Sudoku numbers at the right place on the menu.

        Args:
            num (int): The number to display
            img_x (int): the x coordinate of the corner of the cell
            img_y (int): the y coordinate of the corner of the cell
        """
        font = pygame.font.SysFont("arial", 30)
        text = font.render(str(num), True, BLACK)
        self.display.blit(
            text,
            (
                img_x + (self.spacing - text.get_width()) // 2,
                img_y + (self.spacing - text.get_height()) // 2,
            ),
        )

    def draw_menu_grid(self):
        """Drawing the mini grid in menu
        """
        # drawing lines
        pygame.draw.line(
            self.display,
            BLACK,
            (self.i_left, self.i_top + self.spacing),
            (self.width - self.i_left, self.i_top + self.spacing),
            2,
        )
        pygame.draw.line(
            self.display,
            BLACK,
            (self.i_left, self.i_top + self.spacing * 2),
            (self.width - self.i_left, self.i_top + self.spacing * 2),
            2,
        )
        pygame.draw.line(
            self.display,
            BLACK,
            (self.i_left + self.spacing, self.i_top),
            (self.i_left + self.spacing, self.i_top + self.spacing * 3),
            2,
        )
        pygame.draw.line(
            self.display,
            BLACK,
            (self.i_left + self.spacing * 2, self.i_top),
            (self.i_left + self.spacing * 2, self.i_top + self.spacing * 3),
            2,
        )

    def menu_gui(self):
        """Initialize main menu GUI
        """
        self.display.fill(WHITE)

        self.draw_menu_grid()
        # drawing 1, 3, 5, 7, 9
        self.i_cell(1, self.i_left, self.i_top)
        self.i_cell(3, self.i_left + self.spacing * 2, self.i_top)
        self.i_cell(5, self.i_left + self.spacing, self.i_top + self.spacing)
        self.i_cell(7, self.i_left, self.i_top + self.spacing * 2)
        self.i_cell(9, self.i_left + self.spacing * 2, self.i_top + self.spacing * 2)

        # drawing button and logo
        if self.play_pressed:
            # PLAY button after pressed
            self.display.fill(WHITE_BLUE, self.play_but)
            # EASY button
            self.display.fill(LIGHT_BLUE, self.easy_but)
            temp = (self.bb_height - self.sb_height) // 2
            # MEDIUM button
            self.display.fill(LIGHT_BLUE, self.med_but)
            # HARD button
            self.display.fill(LIGHT_BLUE, self.hard_but)

            font = pygame.font.SysFont("arial", 18)
            text = font.render("EASY", True, BLACK)
            self.display.blit(
                text, (self.sb_xpos + 15, self.bb0_ypos - self.sb_height + 6),
            )
            text = font.render("MEDIUM", True, BLACK)
            self.display.blit(text, (self.sb_xpos + 15, self.bb0_ypos + temp + 6))
            text = font.render("HARD", True, BLACK)
            self.display.blit(
                text, (self.sb_xpos + 15, self.bb0_ypos + self.bb_height + 6)
            )
        else:
            # PLAY button before pressed
            self.display.fill(LIGHT_BLUE, self.play_but)
        # INPUT button
        self.display.fill(LIGHT_BLUE, self.input_but)

        font = pygame.font.SysFont("arial", 40)
        text = font.render("SUDOKU", True, BLACK)
        self.display.blit(text, (self.width // 2 - text.get_width() // 2, 50))

        font = pygame.font.SysFont("arial", 30)
        text = font.render("PLAY", True, BLACK)
        self.display.blit(
            text, (self.width // 2 - text.get_width() // 2, self.bb0_ypos + 10)
        )

        font = pygame.font.SysFont("arial", 30)
        text = font.render("INPUT", True, BLACK)
        self.display.blit(
            text, (self.width // 2 - text.get_width() // 2, self.bb1_ypos + 10)
        )

        if FPS_FLAG:
            fps = str(self.clock.get_fps())
            fps_text = font.render(fps, True, BLACK)
            self.display.blit(fps_text, (470, 610))

        pygame.display.update()

    def start_main(self):
        """Starts the main menu
        """
        self.display = pygame.display.set_mode((self.width, self.height))
        self.clock = pygame.time.Clock()
        self.menu_gui()
        pygame.display.set_caption("Sudoku")
        # main loop of main menu
        while self.running:
            for event in pygame.event.get():
                # enable closing of display
                if event.type == pygame.QUIT:
                    self.running = False
                    pygame.quit()
                    sys.exit()
                # getting position of mouse
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    self.select_button(mouse_pos)

            self.clock.tick(60)
            self.menu_gui()


def main_game():
    """Launches the Sudoku GUI with a random board.
    Creates new boards when no more boards available
    """
    pygame.init()
    SudokuGame()
