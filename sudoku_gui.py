"""This module contains SudokuGui class.
SudokuGui objects contain a representation of the Sudoku
puzzle game.
"""
import copy
import time
from collections import deque

import numpy as np
import pygame

from sudoku_solver import SudokuSolver

# color definitions
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
LIGHT_GREY = (230, 230, 230)
NUM_GREY = (210, 210, 210)
GREY = (150, 150, 150)
LIGHT_BLUE = (160, 180, 220)
BLUE = (50, 50, 200)
RED = (255, 0, 0)
# dimensions of display
WIDTH = 450
HEIGHT = 505


class SudokuGui:
    """Class representing the GUI of a Sudoku board
    """

    def __init__(self, board, fill_own=False):
        self.board = board.copy()
        self.board_backup = self.board.copy()
        self.fill_own = fill_own
        # dictionary to store every position of each number
        self.num_pos = {
            0: set(),
            1: set(),
            2: set(),
            3: set(),
            4: set(),
            5: set(),
            6: set(),
            7: set(),
            8: set(),
            9: set(),
        }
        # 2D numpy array to store the cells
        self.cells = np.empty((9, 9), dtype=Cell)
        # 2D numpy array to store notes of cells
        self.cells_notes = np.empty((9, 9), dtype=set)
        for i in range(9):
            for j in range(9):
                num = self.board[i, j]
                self.cells[i, j] = Cell(num=num, row=i, col=j)
                self.cells_notes[i, j] = set()
                if num != 0:
                    self.num_pos[num].add((i, j))

        # indicating which cell is selected
        self.selected_row = None
        self.selected_col = None
        self.selected_cell = None

        # the width and height of the game display
        self.width = WIDTH
        self.height = HEIGHT
        self.spacing = self.width // 9
        self.display = pygame.display.set_mode((self.width, self.height))

        # False is number input, True is notes input
        self.mode = False
        # determines whether the game is still running
        self.running = True
        # stores the states of the game
        self.state = deque()
        self.time_elapsed = 0
        self.solver = None

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
        row_start = row // 3 * 3
        col_start = col // 3 * 3
        box = self.board[row_start : row_start + 3, col_start : col_start + 3].flatten()
        box_bool = np.sum(box) == sum(set(box))
        return row_bool == col_bool == box_bool == True

    def check_board_validity(self):
        """Checks whether the entire board is valid

        Returns:
            bool: True if board is valid, False otherwise
        """
        # final quality check of validity of solved board
        for i in range(9):
            for j in range(9):
                if not self.check_cell(i, j):
                    return False
        return True

    def sudoku_gui(self):
        """Initialize Sudoku GUI
        """
        # background of GUI should be white
        self.display.fill(WHITE)

        total = self.update_cells()

        # highlight selected row, col, surrounding, and cells with same number
        if self.selected_cell is not None:
            row_top = self.spacing * self.selected_row
            self.display.fill(LIGHT_GREY, pygame.Rect(0, row_top, 450, 50))
            col_left = self.spacing * self.selected_col
            self.display.fill(LIGHT_GREY, pygame.Rect(col_left, 0, 50, 450))
            row_start = self.selected_row // 3 * 3 * self.spacing
            col_start = self.selected_col // 3 * 3 * self.spacing
            self.display.fill(LIGHT_GREY, pygame.Rect(col_start, row_start, 150, 150))

            for pos in self.num_pos[self.board[self.selected_row, self.selected_col]]:
                self.display.fill(
                    NUM_GREY,
                    pygame.Rect(pos[1] * self.spacing, pos[0] * self.spacing, 50, 50),
                )

        thin_line = 1
        thick_line = 3
        # drawing the grey thin grid lines
        for i in range(10):
            pygame.draw.line(
                self.display,
                GREY,
                (0, i * self.spacing),
                (self.width, i * self.spacing),
                thin_line,
            )
            pygame.draw.line(
                self.display,
                GREY,
                (i * self.spacing, 0),
                (i * self.spacing, self.width),
                thin_line,
            )
        # drawing the black thick grid lines
        for i in range(0, 10, 3):
            pygame.draw.line(
                self.display,
                BLACK,
                (0, self.spacing * i),
                (self.width, self.spacing * i),
                thick_line,
            )
            pygame.draw.line(
                self.display,
                BLACK,
                (self.spacing * i, 0),
                (self.spacing * i, self.width),
                thick_line,
            )
        # calling method to draw numbers in cells
        for i, row in enumerate(self.cells):
            for j, cell in enumerate(row):
                cell.color = BLUE if self.check_cell(i, j) else RED
                cell.draw_cell(self.display)

        # back to main menu arrow
        pygame.draw.polygon(self.display, BLACK, ((310, 475), (330, 455), (330, 495)))
        pygame.draw.rect(self.display, BLACK, (325, 465, 40, 20))

        time_font = pygame.font.SysFont("timesnewroman", 30)
        # indicate the time elapsed since the game has started
        text = time_font.render(
            str(self.time_elapsed // 60) + ":" + str(self.time_elapsed % 60),
            True,
            BLACK,
        )
        self.display.blit(text, (390, 460))
        # indicate whether notes mode is ON
        if self.mode:
            font = pygame.font.SysFont("timesnewroman", 30)
            text = font.render("N", True, BLACK)
            self.display.blit(text, (10, 460))

        if self.fill_own:
            font = pygame.font.SysFont("timesnewroman", 30)
            text = font.render("I", True, BLACK)
            self.display.blit(text, (50, 460))

        if total == 81 and self.check_board_validity():
            font = pygame.font.SysFont("timesnewroman", 20)
            text = font.render("CONGRATS!", True, BLACK)
            self.display.blit(text, (self.width / 2 - text.get_width() / 2, 465))

    def update_cells(self):
        """Updates the graphical representation of cells.
        Counts the number of correctly filled in cells

        Returns:
            int: number of correctly filled in cells
        """
        self.num_pos = {
            0: set(),
            1: set(),
            2: set(),
            3: set(),
            4: set(),
            5: set(),
            6: set(),
            7: set(),
            8: set(),
            9: set(),
        }

        total = 0
        for i in range(9):
            for j in range(9):
                cell = self.cells[i, j]
                num = self.board[i, j]
                notes = self.cells_notes[i, j]
                # updating number in cell
                if self.fill_own:
                    cell.base_num = num
                    cell.can_update = True if num == 0 else False
                else:
                    cell.new_num = num
                if num != 0:
                    # clears notes, adds number positions, and counts numbers filled
                    cell.notes.clear()
                    cell.note_using = False
                    self.num_pos[num].add((i, j))
                    total += 1
                else:
                    cell.note_using = True
                    cell.notes = notes

        return total

    def clear_board(self):
        """Clears the sudoku board
        """
        self.board = self.board_backup.copy()
        for i in range(9):
            for j in range(9):
                cell = self.cells[i, j]
                cell.note.clear()
        self.solver = SudokuSolver(self.board)

    def change_selection(self):
        """Changes selected cell according to selected row and col
        """
        try:
            self.selected_cell.selected = False
        except AttributeError:
            pass

        if self.selected_row is None or self.selected_col is None:
            self.selected_cell = None
        else:
            self.selected_cell = self.cells[self.selected_row, self.selected_col]
            self.selected_cell.selected = True

    def select_cell(self, pos):
        """Get selected cell from mouse position and highlight it

        Args:
            pos (tup of 2 ints): pos[0] is the x-position of mouse,
                pos[1] is the y-position of mouse
        """
        if (pos[0] < self.width) and (pos[1] < self.width):
            # if play clicks inside grid, select cell
            col = int(pos[0] // self.spacing)
            row = int(pos[1] // self.spacing)
            self.selected_row = row
            self.selected_col = col

        else:
            # if player clicks outside of grid, deselect cell
            self.selected_row = None
            self.selected_col = None

        self.change_selection()

        if pos[0] > 305 and pos[0] < 370 and pos[1] > 450 and pos[1] < 500:
            # if player clicks on back arrow, return to main menu
            self.running = False

    def move_select_cell(self, direc):
        """Move selection based on keyboard input

        Args:
            direc (str): Can be "left", "up", "right", "down"
        """
        if self.selected_cell is not None:
            if direc == "left" and self.selected_col != 0:
                # select new cell
                self.selected_col = self.selected_col - 1
                self.change_selection()

            elif direc == "top" and self.selected_row != 0:
                # select new cell
                self.selected_row = self.selected_row - 1
                self.change_selection()

            elif direc == "right" and self.selected_col != 8:
                # select new cell
                self.selected_col = self.selected_col + 1
                self.change_selection()

            elif direc == "down" and self.selected_row != 8:
                # select new cell
                self.selected_row = self.selected_row + 1
                self.change_selection()

    def start_game(self):
        """Starts the Sudoku game
        """
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
                        self.solver = SudokuSolver(self.board)
                        self.solver.solve()
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

            self.sudoku_gui()
            pygame.display.update()


class Cell:
    """Class representing a cell in a Sudoku board
    """

    def __init__(self, num, row, col):
        self.base_num = num
        # boolean value to determine whether a cell can be updated (base numbers cannot be updated)
        self.can_update = True if num == 0 else False
        self.new_num = num
        # BLUE if legal value, RED if illegal
        self.color = BLUE
        # using a set to store the notes of a cell
        self.notes = set()
        # boolean value determines whether player is currently using notes
        self.note_using = False
        self.row = row
        self.col = col
        self.width = WIDTH
        self.height = HEIGHT
        self.spacing = self.width / 9
        # boolean value to determine whether a cell is currently selected
        self.selected = False

    def draw_cell(self, display):
        """Draw the number in the cell

        Args:
            display (pygame display): The Sudoku GUI
        """
        # font for the number
        font = pygame.font.SysFont("timesnewroman", 30)
        note_font = pygame.font.SysFont("timesnewroman", 15)
        cell_x = self.spacing * self.col
        cell_y = self.spacing * self.row
        # displaying base number on cell
        if self.base_num != 0:
            text = font.render(str(self.base_num), True, BLACK)
            display.blit(
                text,
                (
                    cell_x + (self.spacing / 2 - text.get_width() / 2),
                    cell_y + (self.spacing / 2 - text.get_height() / 2),
                ),
            )
        # displaying player input number on cell
        if not self.note_using and self.can_update and self.new_num != 0:
            text = font.render(str(self.new_num), True, self.color)
            display.blit(
                text,
                (
                    cell_x + (self.spacing / 2 - text.get_width() / 2),
                    cell_y + (self.spacing / 2 - text.get_height() / 2),
                ),
            )
        # displaying notes on cell
        elif self.note_using and self.can_update:
            for num in self.notes:
                text = note_font.render(str(num), True, GREY)
                note_x = (num - 1) % 3
                note_y = (num - 1) // 3
                display.blit(text, (cell_x + note_x * 15 + 5, cell_y + note_y * 15))
        # draw a red rectangle around selected cell
        if self.selected:
            pygame.draw.rect(
                display, LIGHT_BLUE, (cell_x, cell_y, self.spacing, self.spacing), 2
            )

    def __repr__(self):
        return str(self.base_num)


if __name__ == "__main__":
    pygame.init()
    test_board = np.array(
        [
            [0, 0, 6, 2, 0, 7, 0, 0, 0],
            [0, 0, 0, 0, 0, 5, 6, 0, 0],
            [1, 0, 0, 8, 0, 0, 2, 0, 5],
            [0, 4, 0, 0, 0, 8, 0, 2, 0],
            [2, 9, 0, 0, 0, 0, 0, 0, 0],
            [6, 0, 0, 0, 1, 2, 4, 9, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 3, 7, 0, 0, 0, 0, 1, 9],
            [0, 0, 5, 0, 3, 0, 0, 0, 0],
        ]
    )
    gui = SudokuGui(test_board)
    gui.start_game()
    pygame.quit()
