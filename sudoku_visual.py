"""This module contains SudokuGui class.
SudokuGui objects contain a representation of the Sudoku
puzzle game.
"""
import copy
import os
import random
import time

import numpy as np
import pygame

from sudoku_gui import SudokuGui

NUM_SET = {1, 2, 3, 4, 5, 6, 7, 8, 9}
NUM_LIST = [1, 2, 3, 4, 5, 6, 7, 8, 9]


class SudokuVisualSolver(SudokuGui):
    """Class representing the GUI of a Sudoku board
    """

    def __init__(self, board):
        super().__init__(board)
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
        copied = self.possible[row, col].copy()
        pos = self.possible[row, col]
        if len(pos) == 1:
            self.board[row, col] = pos.pop()
        self.possible[row, col] = copied

    def fill_row(self, row, col):
        """If specified cell has unique number that no other cells in
        this row have, then fill it in

        Args:
            row (int): row of specified cell
            col (int): col of specified cell
        """
        copied = self.possible[row, col].copy()
        pos = self.possible[row, col]
        for index, cell in enumerate(self.possible[row]):
            if index != col:
                pos -= cell
            if not pos:
                break
        if pos:
            self.board[row, col] = pos.pop()
        self.possible[row, col] = copied

    def fill_col(self, row, col):
        """If specified cell has unique number that no other cells in
        this column have, then fill it in

        Args:
            row (int): row of specified cell
            col (int): col of specified cell
        """
        copied = self.possible[row, col].copy()
        pos = self.possible[row, col]
        for index, cell in enumerate(self.possible[:, col]):
            if index != row:
                pos -= cell
            if not pos:
                break
        if pos:
            self.board[row, col] = pos.pop()
        self.possible[row, col] = copied

    def fill_box(self, row, col):
        """If specified cell has unique number that no other cells in
        this box have, then fill it in

        Args:
            row (int): row of specified cell
            col (int): col of specified cell
        """
        row_start = row // 3 * 3
        col_start = col // 3 * 3
        copied = self.possible[row, col].copy()
        pos = self.possible[row, col]
        for index, cell in enumerate(
            self.possible[
                row_start : row_start + 3, col_start : col_start + 3
            ].flatten()
        ):
            if index != (row % 3) * 3 + (col % 3):
                pos -= cell
            if not pos:
                break
        if pos:
            self.board[row, col] = pos.pop()
        self.possible[row, col] = copied

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
        row_start = row // 3 * 3
        col_start = col // 3 * 3
        box_set = NUM_SET - set(
            self.board[row_start : row_start + 3, col_start : col_start + 3].flatten()
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
                    self.sudoku_gui()
                pygame.display.update()

    def guess_cell(self, row, col):
        """Guesses the value of a cell

        Args:
            row (int): row of the cell to guess
            col (int): column of the cell to guess
        """
        cur_val = self.board[row, col]
        for num in range(cur_val + 1, 10):
            self.sudoku_gui()
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
            pygame.display.update()
            pos = self.zeros[self.zero_index]
            if self.zero_index < 0:
                print("NO SOLUTION")
                return False
            if self.guess_cell(pos[0], pos[1]):
                self.zero_index += 1
            else:
                self.zero_index -= 1

        print("VALID")

    def start_game(self):
        """Starts the Sudoku game
        """
        self.display = pygame.display.set_mode((self.width, self.height))
        self.clock = pygame.time.Clock()
        self.sudoku_gui()
        pygame.display.set_caption("Sudoku")
        start = time.time()

        # main loop of Sudoku
        while self.running:
            self.time_elapsed = round(time.time() - start)

            for event in pygame.event.get():
                num = None
                delete = False
                state_changed = False
                # enable closing of display
                if event.type == pygame.QUIT:
                    self.running = False
                    return
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
                    if keys[pygame.K_LEFT]:
                        self.move_select_cell("left")
                    if keys[pygame.K_UP]:
                        self.move_select_cell("top")
                    if keys[pygame.K_RIGHT]:
                        self.move_select_cell("right")
                    if keys[pygame.K_DOWN]:
                        self.move_select_cell("down")
                    if keys[pygame.K_1]:
                        num = 1
                        state_changed = True
                    if keys[pygame.K_2]:
                        num = 2
                        state_changed = True
                    if keys[pygame.K_3]:
                        num = 3
                        state_changed = True
                    if keys[pygame.K_4]:
                        num = 4
                        state_changed = True
                    if keys[pygame.K_5]:
                        num = 5
                        state_changed = True
                    if keys[pygame.K_6]:
                        num = 6
                        state_changed = True
                    if keys[pygame.K_7]:
                        num = 7
                        state_changed = True
                    if keys[pygame.K_8]:
                        num = 8
                        state_changed = True
                    if keys[pygame.K_9]:
                        num = 9
                        state_changed = True
                    if keys[pygame.K_SPACE] and not self.fill_own:
                        self.state.append(
                            (
                                self.board.copy(),
                                copy.deepcopy(self.cells_notes),
                                self.selected_row,
                                self.selected_col,
                            )
                        )
                        self.solve()
                    if keys[pygame.K_c] and keys[pygame.K_LSHIFT]:
                        self.state.append(
                            (
                                self.board.copy(),
                                copy.deepcopy(self.cells_notes),
                                self.selected_row,
                                self.selected_col,
                            )
                        )
                        if self.fill_own:
                            self.board_backup = self.board.copy()
                        self.clear_board()
                    if keys[pygame.K_LCTRL] and keys[pygame.K_z]:
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
                    if self.selected_cell.base_num != 0 and not self.fill_own:
                        self.state.pop()
                    # updating cells (if they can be updated)
                    elif not self.mode:
                        # in play mode, deletes number in selected cell
                        if delete and self.selected_cell.new_num == num:
                            self.board[self.selected_row, self.selected_col] = 0

                        # in input mode, deletes number in selected cell
                        elif delete and self.selected_cell.base_num == num:
                            self.board[self.selected_row, self.selected_col] = 0

                        # adds number to selected cell
                        elif not delete:
                            self.board[self.selected_row, self.selected_col] = num

                            if not self.fill_own:
                                # clearing notes according to updated cell
                                row_start = self.selected_row // 3 * 3
                                col_start = self.selected_col // 3 * 3
                                for row_cell, col_cell, box_cell in zip(
                                    self.cells_notes[self.selected_row],
                                    self.cells_notes[:, self.selected_col],
                                    self.cells_notes[
                                        row_start : row_start + 3,
                                        col_start : col_start + 3,
                                    ].flatten(),
                                ):
                                    row_cell -= {num}
                                    col_cell -= {num}
                                    box_cell -= {num}

                    # updating notes
                    elif self.mode:
                        self.board[self.selected_row, self.selected_col] = 0
                        if delete:
                            self.cells_notes[self.selected_row, self.selected_col] -= {
                                num
                            }
                        elif not delete:
                            self.cells_notes[self.selected_row, self.selected_col].add(
                                num
                            )

            self.clock.tick(60)
            self.sudoku_gui()
            pygame.display.update()


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
    pygame.quit()
