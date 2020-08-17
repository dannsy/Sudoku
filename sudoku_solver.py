"""This module creates SudokuSolver and SudokuRandomSolver classes.
SudokuSolver solves a board using backtracking algorithm, guessing
from 1 to 9 for each cell until the board is solved.

SudokuRandomSolver solves a board using backtracking algorithm, but
guesses randomly for each cell until the board is solved. This solver
is mainly used to generate new boards.
"""
import datetime
import random

import numpy as np

NUM_SET = {1, 2, 3, 4, 5, 6, 7, 8, 9}
NUM_LIST = [1, 2, 3, 4, 5, 6, 7, 8, 9]


def _timer(func):
    """Measure the time taken to execute func

    Args:
        func (def): function to have execution time measured
    """

    def wrapper(*args, **kwargs):
        start_time = datetime.datetime.now()
        func(*args, *kwargs)
        end_time = datetime.datetime.now()
        time_elapsed = str(end_time - start_time)[:-4]
        print(f"Time elapsed for {func.__name__}: {time_elapsed}")

    return wrapper


class SudokuSolver:
    """Given a Sudoku board, solves it using altered backtracking algorithm
    """

    def __init__(self, board):
        self.board = board
        self.possible = np.empty((9, 9), dtype=set)
        self.zeros = []
        self.zero_index = 0
        self.last_time = 0
        self.same = False

    def check_self(self, row, col):
        """If specified cell only has one possible number, fill it in

        Args:
            row (int): row of specified cell
            col (int): col of specified cell
        """
        pos = self.possible[row, col].copy()
        if len(pos) == 1:
            self.board[row, col] = pos.pop()

    def fill_row(self, row, col):
        """If specified cell has unique number that no other cells in
        this row have, then fill it in

        Args:
            row (int): row of specified cell
            col (int): col of specified cell
        """
        pos = self.possible[row, col].copy()
        for index, cell in enumerate(self.possible[row]):
            if index != col:
                pos -= cell
            if not pos:
                break
        else:
            self.board[row, col] = pos.pop()

    def fill_col(self, row, col):
        """If specified cell has unique number that no other cells in
        this column have, then fill it in

        Args:
            row (int): row of specified cell
            col (int): col of specified cell
        """
        pos = self.possible[row, col].copy()
        for index, cell in enumerate(self.possible[:, col]):
            if index != row:
                pos -= cell
            if not pos:
                break
        else:
            self.board[row, col] = pos.pop()

    def fill_box(self, row, col):
        """If specified cell has unique number that no other cells in
        this box have, then fill it in

        Args:
            row (int): row of specified cell
            col (int): col of specified cell
        """
        r_beg = row // 3 * 3
        c_beg = col // 3 * 3
        pos = self.possible[row, col].copy()
        flattened = self.possible[r_beg : r_beg + 3, c_beg : c_beg + 3].flatten()
        for index, cell in enumerate(flattened):
            if index != (row % 3) * 3 + (col % 3):
                pos -= cell
            if not pos:
                break
        else:
            self.board[row, col] = pos.pop()

    def get_possible(self, row, col):
        """Get possible nums for specified cell

        Args:
            row (int): row of specified cell
            col (int): col of specified cell

        Returns:
            set: set containing possible numbers
        """
        row_set = NUM_SET - set(self.board[row])
        col_set = NUM_SET - set(self.board[:, col])
        r_beg = row // 3 * 3
        c_beg = col // 3 * 3
        box_set = NUM_SET - set(
            self.board[r_beg : r_beg + 3, c_beg : c_beg + 3].flatten()
        )

        return row_set.intersection(col_set, box_set)

    def get_zeros(self):
        """Gets all positions of 0s in the board
        """
        counter = 0

        for i, row in enumerate(self.board):
            for j, cell in enumerate(row):
                if cell == 0:
                    self.possible[i, j] = self.get_possible(i, j)
                    counter += 1
                else:
                    self.possible[i, j] = set()

        self.same = self.last_time == counter

        self.last_time = counter

    def preprocess(self):
        """Fills in some cells of the Sudoku board that can be filled in
        """
        while not self.same:
            self.possible = np.empty((9, 9), dtype=set)
            self.get_zeros()

            for i in range(9):
                for j in range(9):
                    self.check_self(i, j)
                    self.fill_row(i, j)
                    self.fill_col(i, j)
                    self.fill_box(i, j)

    def guess_cell(self, row, col):
        """Guesses the value of a cell

        Args:
            row (int): row of the cell to guess
            col (int): column of the cell to guess
        """
        cur_val = self.board[row, col]
        for num in range(cur_val + 1, 10):
            self.board[row, col] = num
            if self.check_cell(row, col):
                return True
        self.board[row, col] = 0
        return False

    def check_cell(self, row, col):
        """Checks whether specified cell is still legal

        Args:
            row (int): row of the cell to check
            col (int): column of the cell to check

        Returns:
            bool: whether updated cell value is legal, True if legal, False otherwise
        """
        # checking row
        row_bool = np.sum(self.board[row]) == sum(set(self.board[row]))
        # checking col
        col_bool = np.sum(self.board[:, col]) == sum(set(self.board[:, col]))
        # checking box
        r_beg = row // 3 * 3
        c_beg = col // 3 * 3
        box = self.board[r_beg : r_beg + 3, c_beg : c_beg + 3].flatten()
        box_bool = np.sum(box) == sum(set(box))
        return row_bool == col_bool == box_bool == True

    @_timer
    def solve(self):
        """Solves the Sudoku board with backtracking
        """
        self.preprocess()

        for i, row in enumerate(self.board):
            for j, cell in enumerate(row):
                if cell == 0:
                    self.zeros.append((i, j))

        while self.zero_index < len(self.zeros):
            pos = self.zeros[self.zero_index]
            if self.zero_index < 0:
                print("NO SOLUTION")
                return False
            if self.guess_cell(pos[0], pos[1]):
                self.zero_index += 1
            else:
                self.zero_index -= 1

        print("VALID")


class SudokuRandomSolver(SudokuSolver):
    """Given a Sudoku board, solves it using backtracking algorithm
    """

    def __init__(self, board, row=None, col=None, num=None):
        super().__init__(board)
        self.time_now = datetime.datetime.now().timestamp()
        # optional exclusion num
        self.row = row
        self.col = col
        self.num = num

    def check_self(self, row, col):
        """If specified cell only has one possible number, fill it in

        Args:
            row (int): row of specified cell
            col (int): col of specified cell
        """
        pos = self.possible[row, col].copy()
        if len(pos) == 1:
            num = pos.pop()
            if self.row == row and self.col == col and self.num == num:
                return False
            self.board[row, col] = num
        return True

    def fill_row(self, row, col):
        """If specified cell has unique number that no other cells in
        this row have, then fill it in

        Args:
            row (int): row of specified cell
            col (int): col of specified cell
        """
        pos = self.possible[row, col].copy()
        for index, cell in enumerate(self.possible[row]):
            if index != col:
                pos -= cell
            if not pos:
                break
        else:
            num = pos.pop()
            if self.row == row and self.col == col and self.num == num:
                return False
            self.board[row, col] = num
        return True

    def fill_col(self, row, col):
        """If specified cell has unique number that no other cells in
        this column have, then fill it in

        Args:
            row (int): row of specified cell
            col (int): col of specified cell
        """
        pos = self.possible[row, col].copy()
        for index, cell in enumerate(self.possible[:, col]):
            if index != row:
                pos -= cell
            if not pos:
                break
        else:
            num = pos.pop()
            if self.row == row and self.col == col and self.num == num:
                return False
            self.board[row, col] = num
        return True

    def fill_box(self, row, col):
        """If specified cell has unique number that no other cells in
        this box have, then fill it in

        Args:
            row (int): row of specified cell
            col (int): col of specified cell
        """
        r_beg = row // 3 * 3
        c_beg = col // 3 * 3
        pos = self.possible[row, col].copy()
        flattened = self.possible[r_beg : r_beg + 3, c_beg : c_beg + 3].flatten()
        for index, cell in enumerate(flattened):
            if index != (row % 3) * 3 + (col % 3):
                pos -= cell
            if not pos:
                break
        else:
            num = pos.pop()
            if self.row == row and self.col == col and self.num == num:
                return False
            self.board[row, col] = num
        return True

    def preprocess(self):
        """Fills in some cells of the Sudoku board that can be filled in
        """
        while not self.same:
            self.possible = np.empty((9, 9), dtype=set)
            self.get_zeros()

            for i in range(9):
                for j in range(9):
                    if not self.check_self(i, j):
                        return False
                    if not self.fill_row(i, j):
                        return False
                    if not self.fill_col(i, j):
                        return False
                    if not self.fill_box(i, j):
                        return False

        # preprocessed
        return True

    def guess_cell(self, row, col):
        """Guesses the value of a cell

        Args:
            row (int): row of the cell to guess
            col (int): column of the cell to guess
        """
        cur_val = self.board[row, col]
        random.seed(self.time_now + row * 9 + col)
        num_list = NUM_LIST.copy()
        random.shuffle(num_list)
        if self.row == row and self.col == col:
            num_list.remove(self.num)
        start = 0 if cur_val == 0 else num_list.index(cur_val) + 1
        for num in num_list[start:]:
            self.board[row, col] = num
            if self.check_cell(row, col):
                return True
        self.board[row, col] = 0
        return False

    def solve(self):
        """Solves the Sudoku board with backtracking
        """
        if not self.preprocess():
            # print("NO SOLUTION")
            return False

        for i, row in enumerate(self.board):
            for j, cell in enumerate(row):
                if cell == 0:
                    self.zeros.append((i, j))

        while self.zero_index < len(self.zeros):
            pos = self.zeros[self.zero_index]
            if self.zero_index < 0:
                # print("NO SOLUTION")
                return False
            if self.guess_cell(pos[0], pos[1]):
                self.zero_index += 1
            else:
                self.zero_index -= 1

        # final quality check of validity of solved board
        for i in range(9):
            for j in range(9):
                if not self.check_cell(i, j):
                    # print("NOT VALID")
                    return False

        # print("VALID")
        return True


if __name__ == "__main__":
    # 2D list to represent the board, with value 0 representing empty cells
    # 1.65 sec
    test_board = np.array(
        [
            [9, 8, 4, 0, 0, 0, 5, 0, 1],
            [0, 0, 0, 5, 0, 0, 0, 0, 7],
            [0, 0, 0, 0, 0, 0, 0, 0, 9],
            [0, 0, 0, 0, 1, 0, 0, 0, 0],
            [0, 2, 0, 7, 0, 3, 1, 0, 0],
            [5, 6, 0, 0, 0, 0, 0, 0, 0],
            [8, 0, 0, 0, 0, 0, 4, 9, 6],
            [0, 0, 0, 0, 9, 0, 0, 0, 0],
            [1, 0, 0, 2, 8, 0, 0, 0, 0],
        ]
    )

    # test_board = np.array(
    #     [
    #         [0, 0, 6, 2, 0, 7, 0, 0, 0],
    #         [0, 0, 0, 0, 0, 5, 6, 0, 0],
    #         [1, 0, 0, 8, 0, 0, 2, 0, 5],
    #         [0, 4, 0, 0, 0, 8, 0, 2, 0],
    #         [2, 9, 0, 0, 0, 0, 0, 0, 0],
    #         [6, 0, 0, 0, 1, 2, 4, 9, 0],
    #         [0, 0, 0, 0, 0, 0, 0, 0, 0],
    #         [0, 3, 7, 0, 0, 0, 0, 1, 9],
    #         [0, 0, 5, 0, 3, 0, 0, 0, 0],
    #     ]
    # )

    # # 1 sec
    # test_board = np.array(
    #     [
    #         [7, 0, 0, 0, 0, 9, 0, 0, 3],
    #         [0, 9, 0, 1, 0, 0, 8, 0, 0],
    #         [0, 1, 0, 0, 0, 7, 0, 0, 0],
    #         [0, 3, 0, 4, 0, 0, 0, 8, 0],
    #         [6, 0, 0, 0, 8, 0, 0, 0, 1],
    #         [0, 7, 0, 0, 0, 2, 0, 3, 0],
    #         [0, 0, 0, 5, 0, 0, 0, 1, 0],
    #         [0, 0, 4, 0, 0, 3, 0, 9, 0],
    #         [5, 0, 0, 7, 0, 0, 0, 0, 2],
    #     ]
    # )

    # # HARDEST SUDOKU, 8 seconds
    # test_board = np.array(
    #     [
    #         [8, 0, 0, 0, 0, 0, 0, 0, 0],
    #         [0, 0, 3, 6, 0, 0, 0, 0, 0],
    #         [0, 7, 0, 0, 9, 0, 2, 0, 0],
    #         [0, 5, 0, 0, 0, 7, 0, 0, 0],
    #         [0, 0, 0, 0, 4, 5, 7, 0, 0],
    #         [0, 0, 0, 1, 0, 0, 0, 3, 0],
    #         [0, 0, 1, 0, 0, 0, 0, 6, 8],
    #         [0, 0, 8, 5, 0, 0, 0, 1, 0],
    #         [0, 9, 0, 0, 0, 0, 4, 0, 0],
    #     ]
    # )

    solver = SudokuSolver(test_board)
    solver.solve()

    print(solver.board)
