"""This module contains Sudoku generator class, which creates
randomized 2D 9x9 Sudoku boards.
"""
import os
import random
from pathlib import Path

import numpy as np

from sudoku_solver import SudokuRandomSolver

NUM_RANGE = list(range(81))


class SudokuGenerator:
    """Generates a Sudoku board
    """

    def __init__(self, total_cells=30):
        solver = SudokuRandomSolver(np.zeros((9, 9), dtype=int))
        solver.solve()
        print(solver.board)
        self.board = solver.board.copy()
        self.num_range = NUM_RANGE.copy()
        self.remove_order = []
        self.to_remove = 81 - total_cells
        self.generate_order()
        self.remove_num()

    def generate_order(self):
        """Generates the order of numbers to remove
        """
        for _ in range(81):
            num = random.choice(self.num_range)
            self.num_range.remove(num)
            self.remove_order.append((num // 9, num % 9))

    def remove_num(self):
        """Removes a number and checks whether board is still legal.
        If not, restore number
        """
        index = 0
        for pos in self.remove_order:
            if index >= self.to_remove:
                break

            row, col = pos[0], pos[1]
            num = self.board[row, col]
            self.board[row, col] = 0

            test_solve = SudokuRandomSolver(self.board.copy(), row, col, num)
            if test_solve.solve():
                self.board[row, col] = num
            else:
                index += 1


def main(num, difficulty):
    """Generates num random boards with specified difficulty

    Args:
        num (int): number of boards to generate
        difficulty (str): "easy", "medium", or "hard"
    """
    Path(os.path.join(os.getcwd(), "boards", "easy")).mkdir(parents=True, exist_ok=True)
    Path(os.path.join(os.getcwd(), "boards", "medium")).mkdir(
        parents=True, exist_ok=True
    )
    Path(os.path.join(os.getcwd(), "boards", "hard")).mkdir(parents=True, exist_ok=True)

    difficulty_dir = os.path.join(os.getcwd(), "boards", difficulty)
    board_list = os.listdir(difficulty_dir)
    num_list = [int(f.split("_")[0]) for f in board_list]

    difficulty_dict = {"easy": 38, "medium": 30, "hard": 25}

    if num_list:
        max_num = max(num_list)
        max_num += 1
    else:
        max_num = 0

    for i in range(num):
        print(i)
        generated_board = SudokuGenerator(difficulty_dict[difficulty])
        print(generated_board.board)
        print()
        np.save(
            os.path.join(difficulty_dir, f"{max_num + i}_board.npy"),
            generated_board.board,
        )


if __name__ == "__main__":
    main(10, "easy")
