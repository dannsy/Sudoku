"""This module contains SudokuGui class.
SudokuGui objects contain a representation of the Sudoku
puzzle game.
"""
import copy
import sys
from collections import deque

import numpy as np
import pygame

from sudoku.utils.sudoku_solver import SudokuSolver

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
WIDTH = 540
HEIGHT = 660

FPS_FLAG = False


class SudokuGui:
    """Class representing the GUI of a Sudoku board
    """

    width = WIDTH
    height = HEIGHT
    spacing = width // 9
    top_pad = spacing

    input_area = pygame.Rect(0, top_pad, width, width)

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
        count = 0
        for i in range(9):
            for j in range(9):
                num = self.board[i, j]
                self.cells[i, j] = Cell(num=num, row=i, col=j)
                self.cells_notes[i, j] = set()
                if num != 0:
                    self.num_pos[num].add((i, j))
                    count += 1

        if count >= 38:
            self.difficulty = "EASY"
        elif count >= 30:
            self.difficulty = "MEDIUM"
        else:
            self.difficulty = "HARD"

        # indicating which cell is selected
        self.selected_row = None
        self.selected_col = None
        self.selected_cell = None

        # False is number input, True is notes input
        self.mode = False
        # determines whether the game is still running
        self.running = True
        self.quitted = False
        # stores the states of the game
        self.state = deque()
        self.time_elapsed = 0
        self.clock = None
        self.solver = None
        self.display = None

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

    def clear_board(self):
        """Clears the sudoku board
        """
        self.board = self.board_backup.copy()
        for i in range(9):
            for j in range(9):
                cell = self.cells[i, j]
                cell.notes.clear()
        self.solver = None

    def select_cell(self, pos):
        """Get selected cell from mouse position and highlight it

        Args:
            pos (tup of 2 ints): pos[0] is the x-position of mouse,
                pos[1] is the y-position of mouse
        """
        if self.input_area.collidepoint(pos):
            # if play clicks inside grid, select cell
            col = pos[0] // self.spacing
            row = (pos[1] - self.top_pad) // self.spacing
            self.selected_row = row
            self.selected_col = col

        else:
            # if player clicks outside of grid, deselect cell
            self.selected_row = None
            self.selected_col = None

        self.change_selection()

        if pos[0] > 10 and pos[0] < 60 and pos[1] > 10 and pos[1] < 50:
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

    def detect_arrow_pressed(self, keys):
        """Detects keyboard arrow input

        Args:
            keys (dict): dictionary containing keys that have been pressed
        """
        arrow_keys = [pygame.K_UP, pygame.K_DOWN, pygame.K_RIGHT, pygame.K_LEFT]
        directions = ["top", "down", "right", "left"]
        for key, direc in zip(arrow_keys, directions):
            if keys[key]:
                self.move_select_cell(direc)

    @staticmethod
    def detect_num_pressed(keys):
        """Detects keyboard number input

        Args:
            keys (dict): dictionary containing keys that have been pressed

        Returns:
            (bool, int): True if number has been pressed, and return number
        """
        start_num = pygame.K_1
        for key, num in zip(range(start_num, start_num + 10), range(1, 10)):
            if keys[key]:
                return True, num

        return False, None

    def update_num_notes(self, num, delete):
        """Handles the logic behind updating cell values and replacing notes

        Args:
            num (int): new number to be put into cell, note or not
            delete (bool): if True, delete num in selected cell
        """
        if self.selected_cell.base_num != 0 and not self.fill_own:
            # undo previously added state if player writing to cell with default value
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
                    r_beg = self.selected_row // 3 * 3
                    c_beg = self.selected_col // 3 * 3
                    zipped = zip(
                        self.cells_notes[self.selected_row],
                        self.cells_notes[:, self.selected_col],
                        self.cells_notes[
                            r_beg : r_beg + 3, c_beg : c_beg + 3
                        ].flatten(),
                    )
                    for row_cell, col_cell, box_cell in zipped:
                        row_cell -= {num}
                        col_cell -= {num}
                        box_cell -= {num}

        # updating notes
        elif self.mode:
            self.board[self.selected_row, self.selected_col] = 0
            if delete:
                self.cells_notes[self.selected_row, self.selected_col] -= {num}
            else:
                self.cells_notes[self.selected_row, self.selected_col].add(num)

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
                    # solve board immediately
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
                if keys[pygame.K_v] and not self.fill_own:
                    from sudoku.utils.sudoku_visual import SudokuVisualSolver

                    # solve board visually
                    self.state.append(
                        (
                            self.board.copy(),
                            copy.deepcopy(self.cells_notes),
                            self.selected_row,
                            self.selected_col,
                        )
                    )
                    self.solver = SudokuVisualSolver(self.board, self.display)
                    self.solver.solve()
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

    def draw_select_fill(self):
        """Highlight selected cell's row, column, surrounding, and cells with same number
        """
        if self.selected_cell is not None:
            # highlighting row
            r_top = self.spacing * self.selected_row + self.top_pad
            row_rect = pygame.Rect(0, r_top, self.width, self.spacing)
            self.display.fill(LIGHT_GREY, row_rect)

            # highlighting column
            c_left = self.spacing * self.selected_col
            col_rect = pygame.Rect(c_left, self.top_pad, self.spacing, self.width)
            self.display.fill(LIGHT_GREY, col_rect)

            # highlighting box
            r_beg = self.selected_row // 3 * 3 * self.spacing + self.top_pad
            c_beg = self.selected_col // 3 * 3 * self.spacing
            box_rect = pygame.Rect(c_beg, r_beg, self.spacing * 3, self.spacing * 3)
            self.display.fill(LIGHT_GREY, box_rect)

            # highlighting cells with same number
            for pos in self.num_pos[self.board[self.selected_row, self.selected_col]]:
                self.display.fill(
                    NUM_GREY,
                    pygame.Rect(
                        pos[1] * self.spacing,
                        self.top_pad + pos[0] * self.spacing,
                        self.spacing,
                        self.spacing,
                    ),
                )

    def draw_grid_lines(self):
        """Drawing the grid lines of the Sudoku board
        """
        # drawing the grey thin grid lines
        for i in range(10):
            # horizontal lines
            start_pos = (0, i * self.spacing + self.top_pad)
            end_pos = (self.width, i * self.spacing + self.top_pad)
            pygame.draw.line(self.display, GREY, start_pos, end_pos, 1)

            # vertical lines
            start_pos = (i * self.spacing, self.top_pad)
            end_pos = (i * self.spacing, self.width + self.top_pad)
            pygame.draw.line(self.display, GREY, start_pos, end_pos, 1)
        # drawing the black thick grid lines
        for i in range(0, 10, 3):
            # horizontal lines
            start_pos = (0, i * self.spacing + self.top_pad)
            end_pos = (self.width, i * self.spacing + self.top_pad)
            pygame.draw.line(self.display, BLACK, start_pos, end_pos, 3)

            # vertical lines
            start_pos = (i * self.spacing, self.top_pad)
            end_pos = (i * self.spacing, self.width + self.top_pad)
            pygame.draw.line(self.display, BLACK, start_pos, end_pos, 3)

    def draw_numbers(self):
        """Drawing numbers on the board
        """
        for i, row in enumerate(self.cells):
            for j, cell in enumerate(row):
                cell.color = BLUE if self.check_cell(i, j) else RED
                cell.draw_cell(self.display)

    def draw_peripherals(self, total):
        """Drawing some UI elements like time elapsed, back arrow etc.

        Args:
            total (int): total amount of correctly filled in cells
        """
        # back to main menu arrow
        pygame.draw.polygon(self.display, BLACK, ((10, 30), (30, 10), (30, 50)))
        pygame.draw.rect(self.display, BLACK, (20, 20, 40, 20))

        font = pygame.font.SysFont("timesnewroman", 30)
        # indicate the time elapsed since the game has started
        text = font.render(
            f"{(self.time_elapsed // 60):02}:{(self.time_elapsed % 60):02}",
            True,
            BLACK,
        )
        self.display.blit(text, (470, 15))

        if FPS_FLAG:
            # fps counter
            fps = str(self.clock.get_fps())
            fps_text = font.render(fps, True, BLACK)
            self.display.blit(fps_text, (470, 610))

        if self.fill_own:
            text = font.render("INPUT", True, BLACK)
        else:
            text = font.render(self.difficulty, True, BLACK)
        self.display.blit(text, (self.width // 2 - text.get_width() // 2, 15))

        # indicate whether notes mode is ON
        if self.mode:
            text = font.render("N", True, BLACK)
            self.display.blit(text, (10, 610))

        if self.fill_own:
            text = font.render("I", True, BLACK)
            self.display.blit(text, (50, 610))

        if total == 81 and self.check_board_validity():
            text = font.render("CONGRATS!", True, BLACK)
            self.display.blit(text, (self.width // 2 - text.get_width() // 2, 610))

    def update_gui(self):
        """Updates Sudoku GUI
        """
        # background of GUI should be white
        self.display.fill(WHITE)

        total = self.update_cells()

        self.draw_select_fill()
        self.draw_grid_lines()
        self.draw_numbers()
        self.draw_peripherals(total)

        pygame.display.update()

    def start_game(self):
        """Starts the Sudoku game
        """
        self.display = pygame.display.set_mode((self.width, self.height))
        self.clock = pygame.time.Clock()
        self.update_gui()
        pygame.display.set_caption("Sudoku")
        start = pygame.time.get_ticks()

        # main loop of Sudoku
        while self.running:
            self.time_elapsed = int((pygame.time.get_ticks() - start) / 1000)

            self.check_events()

            self.clock.tick(60)
            self.update_gui()


class Cell:
    """Class representing a cell in a Sudoku board
    """

    width = WIDTH
    height = HEIGHT
    spacing = width // 9
    top_pad = spacing

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
        self.cell_x = self.spacing * self.col
        self.cell_y = self.spacing * self.row + self.top_pad
        # font for cell
        self.font = pygame.font.SysFont("timesnewroman", 34)
        self.note_font = pygame.font.SysFont("timesnewroman", 20)
        self.text_x_initial = self.cell_x + self.spacing // 2
        self.text_y_initial = self.cell_y + self.spacing // 2
        # boolean value to determine whether a cell is currently selected
        self.selected = False

    def get_num_pos(self, text):
        """Get the correct text position as a tuple

        Args:
            text (pygame font render): text to be displayed, number

        Returns:
            tuple of int: contains the x and y position of text position
        """
        text_x = self.text_x_initial - text.get_width() // 2
        text_y = self.text_y_initial - text.get_height() // 2
        return text_x, text_y

    def draw_cell(self, display):
        """Draw the number in the cell

        Args:
            display (pygame display): The Sudoku GUI
        """
        # displaying base number on cell
        if self.base_num != 0:
            text = self.font.render(str(self.base_num), True, BLACK)
            display.blit(text, self.get_num_pos(text))
        # displaying player input number on cell
        if not self.note_using and self.can_update and self.new_num != 0:
            text = self.font.render(str(self.new_num), True, self.color)
            display.blit(text, self.get_num_pos(text))
        # displaying notes on cell
        elif self.note_using and self.can_update:
            for num in self.notes:
                text = self.note_font.render(str(num), True, GREY)
                note_x = (num - 1) % 3
                note_y = (num - 1) // 3
                display.blit(
                    text, (self.cell_x + note_x * 19 + 6, self.cell_y + note_y * 19)
                )
        # draw a red rectangle around selected cell
        if self.selected:
            pygame.draw.rect(
                display,
                LIGHT_BLUE,
                (self.cell_x, self.cell_y, self.spacing, self.spacing),
                2,
            )

    def __repr__(self):
        return str(self.base_num)
