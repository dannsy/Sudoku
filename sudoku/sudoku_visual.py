"""This module contains SudokuGui class.
SudokuGui objects contain a representation of the Sudoku
puzzle game.
"""
import copy
import os
import random
import sys

import numpy as np
import pygame

from sudoku_gui import SudokuGui
from sudoku_solver import SudokuSolver


class SudokuVisualSolver(SudokuGui, SudokuSolver):
    """Class representing the GUI of a Sudoku board
    with a visualized solving process
    """

    def __init__(self, board):
        SudokuGui.__init__(self, board)
        SudokuSolver.__init__(self, board)

    def preprocess(self):
        """Fills in some cells of the Sudoku board that can be filled in
        """
        while not self.same:

            for event in pygame.event.get():
                # enable closing of display
                if event.type == pygame.QUIT:
                    self.running = False
                    pygame.quit()
                    sys.exit()

            self.possible = np.empty((9, 9), dtype=set)
            self.get_zeros()

            for i in range(9):
                for j in range(9):
                    self.check_self(i, j)
                    self.fill_row(i, j)
                    self.fill_col(i, j)
                    self.fill_box(i, j)
                    self.update_gui()

    def guess_cell(self, row, col):
        """Guesses the value of a cell

        Args:
            row (int): row of the cell to guess
            col (int): column of the cell to guess
        """
        cur_val = self.board[row, col]
        for num in range(cur_val + 1, 10):
            self.update_gui()
            self.board[row, col] = num
            if self.check_cell(row, col):
                return True
        self.board[row, col] = 0
        return False

    def solve(self):
        """Solves the Sudoku board with backtracking
        """
        self.preprocess()

        for i, row in enumerate(self.board):
            for j, cell in enumerate(row):
                if cell == 0:
                    self.zeros.append((i, j))

        while self.zero_index < len(self.zeros):

            for event in pygame.event.get():
                # enable closing of display
                if event.type == pygame.QUIT:
                    self.running = False
                    pygame.quit()
                    sys.exit()

            pos = self.zeros[self.zero_index]
            if self.zero_index < 0:
                print("NO SOLUTION")
                return False
            if self.guess_cell(pos[0], pos[1]):
                self.zero_index += 1
            else:
                self.zero_index -= 1

        print("VALID")

    def check_events(self):
        """Check pygame events during main game loop
        """
        for event in pygame.event.get():
            num = None
            delete = False
            state_changed = False
            # enable closing of display
            if event.type == pygame.QUIT:
                self.running = False
                pygame.quit()
                sys.exit()
            # getting position of mouse
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                self.select_cell(mouse_pos)
            # getting keyboard input
            if event.type == pygame.KEYDOWN:
                keys = pygame.key.get_pressed()
                if keys[pygame.K_n] and not self.fill_own:
                    self.mode = not self.mode
                if keys[pygame.K_d]:
                    delete = True
                if keys[pygame.K_i]:
                    self.fill_own = False
                    self.board_backup = self.board.copy()

                # getting arrow key pressed
                self.detect_arrow_pressed(keys)
                # getting number pressed
                state_changed, num = self.detect_num_pressed(keys)

                if keys[pygame.K_SPACE] and not self.fill_own:
                    # solve board command
                    self.state.append(
                        (
                            self.board.copy(),
                            copy.deepcopy(self.cells_notes),
                            self.selected_row,
                            self.selected_col,
                        )
                    )
                    self.solve()
                if keys[pygame.K_c] and keys[pygame.K_LCTRL]:
                    # clear board command
                    self.state.append(
                        (
                            self.board.copy(),
                            copy.deepcopy(self.cells_notes),
                            self.selected_row,
                            self.selected_col,
                        )
                    )
                    self.clear_board()
                if keys[pygame.K_z] and keys[pygame.K_LCTRL]:
                    try:
                        (
                            self.board,
                            self.cells_notes,
                            self.selected_row,
                            self.selected_col,
                        ) = self.state.pop()
                        self.change_selection()
                    except IndexError:
                        self.clear_board()
                if keys[pygame.K_ESCAPE]:
                    self.running = False
                    return
            if state_changed:
                self.state.append(
                    (
                        self.board.copy(),
                        copy.deepcopy(self.cells_notes),
                        self.selected_row,
                        self.selected_col,
                    )
                )

            if num is not None and self.selected_cell is not None:
                self.update_num_notes(num, delete)


def main(difficulty):
    """Choose a random board from generated boards
    """
    print(difficulty)
    try:
        difficulty_dir = os.path.join(os.getcwd(), "boards", difficulty)
        board_list = os.listdir(difficulty_dir)
        chosen = random.choice(board_list)
        print(chosen)
        generated_board = np.load(os.path.join(difficulty_dir, chosen))
        gui = SudokuVisualSolver(generated_board)
        gui.start_game()
        os.remove(os.path.join(difficulty_dir, chosen))
    except (FileNotFoundError, IndexError):
        print("Not enough boards, please generate new ones")


if __name__ == "__main__":
    pygame.init()
    main(random.choice(["easy", "medium", "hard"]))
