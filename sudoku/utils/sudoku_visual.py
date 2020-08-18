"""This module contains SudokuGui class.
SudokuGui objects contain a representation of the Sudoku
puzzle game.
"""
import sys

import numpy as np
import pygame

from sudoku.utils.sudoku_gui import SudokuGui
from sudoku.utils.sudoku_solver import SudokuSolver


class SudokuVisualSolver(SudokuGui, SudokuSolver):
    """Class representing a solver for a Sudoku board
    with a visualized solving process
    """

    def __init__(self, board, display):
        SudokuGui.__init__(self, board)
        SudokuSolver.__init__(self, board)
        self.display = display

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
