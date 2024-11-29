from cell_object import SudokuCell
from history_stack import HistoryStack


class SudokuPuzzle:
    def __init__(self, size: int = 9):
        if size not in [4, 9]:  # Allow only 4x4 or 9x9 Sudoku boards
            raise ValueError("Only 4x4 and 9x9 Sudoku puzzles are supported.")
        self.size = size
        self.grid = [[SudokuCell((row, col), correct_value=None)
                      for col in range(size)] for row in range(size)]
        self.history = HistoryStack()

    # Method to initialize the puzzle with correct values
    def set_correct_values(self, correct_values: list):
        if len(correct_values) != self.size or any(len(row) != self.size for row in correct_values):
            raise ValueError(
                "Correct values must match the size of the puzzle.")
        for row in range(self.size):
            for col in range(self.size):
                self.grid[row][col].set_correct_value(correct_values[row][col])

    # Get cell at specific location
    def get_cell(self, row: int, col: int):
        return self.grid[row][col]

    # Set inserted value for a specific cell
    def set_inserted_value(self, row: int, col: int, value: int):
        self.grid[row][col].set_inserted_value(value)

    # Check if the puzzle is solved
    def is_solved(self):
        for row in self.grid:
            for cell in row:
                if not cell.get_is_correct():
                    return False
        return True

    def is_filled(self):
        for row in self.grid:
            for cell in row:
                if cell.get_inserted_value() == None:
                    return False
        return True

    def get_puzzle_state(self):
        """
        Get a snapshot of the current puzzle grid.
        :return: A list of lists representing the grid's current state.
        """
        return [[cell.get_inserted_value() for cell in row] for row in self.grid]

    def undo(self):
        """
        Undo the most recent action by restoring the previous puzzle state.
        """
        last_entry = self.history.pop()
        if last_entry:
            action = last_entry["action"]
            puzzle_state = last_entry["puzzle_state"]
            # Restore the puzzle state
            for row in range(self.size):
                for col in range(self.size):
                    self.grid[row][col].set_inserted_value(
                        puzzle_state[row][col])


def undo_until_no_incorrect(self):
    """
    Undo actions until there are no incorrect cells in the puzzle or the history stack is empty.
    """
    while self.history.peek() and any(
        cell.get_correctness() is False
        for row in self.grid
        for cell in row
    ):
        self.undo()

    # Display methods for testing

    def display(self):
        for row in self.grid:
            print([cell.get_inserted_value() or "." for cell in row])

    # Display the puzzle's correct solution
    def display_solution(self):
        for row in self.grid:
            print([cell.get_correct_value() for cell in row])
