"""This module contains SudokuGame class.
Starts the Sudoku game.
"""
import multiprocessing
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
WIDTH = 540
HEIGHT = 660

FPS_FLAG = False


class SudokuGame:
    """Creates the main menu launches game depending on player choice
    """

    width = WIDTH
    height = HEIGHT
    display = None

    bigbut_xpos = int(width / 3)
    bigbut0_ypos = int(height * 0.7)
    bigbut1_ypos = int(height * 0.8)
    bigbut_height = int(height * 0.1 - 6)
    bigbut_width = int(width / 3)

    smallbut_xpos = int(width / 3 * 2 + 10)
    smallbut_width = int(bigbut_width * 0.6)
    smallbut_height = int(bigbut_height * 0.6)

    image_top = int(height * 0.2)
    image_left = int(width * 0.25)
    spacing = int(width * 0.5 / 3)

    def __init__(self):
        self.running = True
        self.play_pressed = False
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
                p1 = multiprocessing.Process(target=main, args=[10, difficulty])
                p1.start()
                # main(5, difficulty)
        except (FileNotFoundError, IndexError):
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
        temp = (self.bigbut_height - self.smallbut_height) // 2
        # PLAY
        if (
            pos[0] > self.bigbut_xpos
            and pos[0] < self.bigbut_xpos + self.bigbut_width
            and pos[1] > self.bigbut0_ypos
            and pos[1] < self.bigbut0_ypos + self.bigbut_height
        ):
            self.play_pressed = True
        # INPUT
        elif (
            pos[0] > self.bigbut_xpos
            and pos[0] < self.bigbut_xpos + self.bigbut_width
            and pos[1] > self.bigbut1_ypos
            and pos[1] < self.bigbut1_ypos + self.bigbut_height
        ):
            sudoku_game = SudokuGui(np.zeros((9, 9), dtype=int), fill_own=True)
            sudoku_game.start_game()
        # EASY
        elif (
            self.play_pressed
            and pos[0] > self.smallbut_xpos
            and pos[0] < self.smallbut_xpos + self.smallbut_width
            and pos[1] > self.bigbut0_ypos - self.smallbut_height
            and pos[1] < self.bigbut0_ypos
        ):
            self.choose_board("easy")
            sudoku_game = SudokuGui(self.generated_board)
            sudoku_game.start_game()
            self.play_pressed = False
        # MEDIUM
        elif (
            self.play_pressed
            and pos[0] > self.smallbut_xpos
            and pos[0] < self.smallbut_xpos + self.smallbut_width
            and pos[1] > self.bigbut0_ypos + temp
            and pos[1] < self.bigbut0_ypos + temp + self.smallbut_height
        ):
            self.choose_board("medium")
            sudoku_game = SudokuGui(self.generated_board)
            sudoku_game.start_game()
            self.play_pressed = False
        # HARD
        elif (
            self.play_pressed
            and pos[0] > self.smallbut_xpos
            and pos[0] < self.smallbut_xpos + self.smallbut_width
            and pos[1] > self.bigbut0_ypos + self.bigbut_height
            and pos[1] < self.bigbut0_ypos + self.bigbut_height + self.smallbut_height
        ):
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
            text, (img_x - text.get_width() // 2, img_y - text.get_height() // 2),
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
            (self.width - self.image_left, self.image_top + self.spacing),
            2,
        )
        pygame.draw.line(
            self.display,
            BLACK,
            (self.image_left, self.image_top + self.spacing * 2),
            (self.width - self.image_left, self.image_top + self.spacing * 2),
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
            1, self.image_left + self.spacing // 2, self.image_top + self.spacing // 2
        )
        self.image_cell(
            3,
            self.image_left + self.spacing * 5 // 2,
            self.image_top + self.spacing // 2,
        )
        self.image_cell(
            5,
            self.image_left + self.spacing * 3 // 2,
            self.image_top + self.spacing * 3 // 2,
        )
        self.image_cell(
            7,
            self.image_left + self.spacing // 2,
            self.image_top + self.spacing * 5 // 2,
        )
        self.image_cell(
            9,
            self.image_left + self.spacing * 5 // 2,
            self.image_top + self.spacing * 5 // 2,
        )

        # drawing button and logo
        if self.play_pressed:
            # PLAY button after pressed
            self.display.fill(
                WHITE_BLUE,
                pygame.Rect(
                    self.bigbut_width,
                    self.bigbut0_ypos,
                    self.bigbut_width,
                    self.bigbut_height,
                ),
            )
            # EASY button
            self.display.fill(
                LIGHT_BLUE,
                pygame.Rect(
                    self.smallbut_xpos,
                    self.bigbut0_ypos - self.smallbut_height,
                    self.smallbut_width,
                    self.smallbut_height,
                ),
            )
            temp = (self.bigbut_height - self.smallbut_height) // 2
            # MEDIUM button
            self.display.fill(
                LIGHT_BLUE,
                pygame.Rect(
                    self.smallbut_xpos,
                    self.bigbut0_ypos + temp,
                    self.smallbut_width,
                    self.smallbut_height,
                ),
            )
            # HARD button
            self.display.fill(
                LIGHT_BLUE,
                pygame.Rect(
                    self.smallbut_xpos,
                    self.bigbut0_ypos + self.bigbut_height,
                    self.smallbut_width,
                    self.smallbut_height,
                ),
            )
            font = pygame.font.SysFont("arial", 18)
            text = font.render("EASY", True, BLACK)
            self.display.blit(
                text,
                (self.smallbut_xpos + 15, self.bigbut0_ypos - self.smallbut_height + 6),
            )
            text = font.render("MEDIUM", True, BLACK)
            self.display.blit(
                text, (self.smallbut_xpos + 15, self.bigbut0_ypos + temp + 6)
            )
            text = font.render("HARD", True, BLACK)
            self.display.blit(
                text,
                (self.smallbut_xpos + 15, self.bigbut0_ypos + self.bigbut_height + 6),
            )
        else:
            # PLAY button before pressed
            self.display.fill(
                LIGHT_BLUE,
                pygame.Rect(
                    self.bigbut_width,
                    self.bigbut0_ypos,
                    self.bigbut_width,
                    self.bigbut_height,
                ),
            )
        # INPUT button
        self.display.fill(
            LIGHT_BLUE,
            pygame.Rect(
                self.bigbut_width,
                self.bigbut1_ypos,
                self.bigbut_width,
                self.bigbut_height,
            ),
        )

        font = pygame.font.SysFont("arial", 40)
        text = font.render("SUDOKU", True, BLACK)
        self.display.blit(text, (self.width // 2 - text.get_width() // 2, 50))

        font = pygame.font.SysFont("arial", 30)
        text = font.render("PLAY", True, BLACK)
        self.display.blit(
            text, (self.width // 2 - text.get_width() // 2, self.bigbut0_ypos + 10)
        )

        font = pygame.font.SysFont("arial", 30)
        text = font.render("INPUT", True, BLACK)
        self.display.blit(
            text, (self.width // 2 - text.get_width() // 2, self.bigbut1_ypos + 10)
        )

        if FPS_FLAG:
            fps = str(self.clock.get_fps())
            fps_text = font.render(fps, True, BLACK)
            self.display.blit(fps_text, (470, 610))

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
                    return
                # getting position of mouse
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    self.select_button(mouse_pos)
                # # getting keyboard input
                # if event.type == pygame.KEYDOWN:
                #     keys = pygame.key.get_pressed()

            self.clock.tick(60)
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
