import unittest
from cell_object import SudokuCell
from puzzle_object import SudokuPuzzle


class TestSudokuCell(unittest.TestCase):
    def setUp(self):
        self.cell = SudokuCell((0, 0), correct_value=5)

    def test_initialization(self):
        self.assertEqual(self.cell.get_location(), (0, 0))
        self.assertEqual(self.cell.get_correct_value(), 5)
        self.assertIsNone(self.cell.get_inserted_value())
        self.assertFalse(self.cell.get_is_correct())
        self.assertFalse(self.cell.get_is_initialized())
        self.assertEqual(self.cell.get_notes(), [])

    def test_set_inserted_value(self):
        self.cell.set_inserted_value(5)
        self.assertEqual(self.cell.get_inserted_value(), 5)
        self.assertTrue(self.cell.get_is_correct())

    def test_notes(self):
        self.cell.add_note(3)
        self.cell.add_note(7)
        self.assertEqual(self.cell.get_notes(), [3, 7])
        self.cell.remove_note(3)
        self.assertEqual(self.cell.get_notes(), [7])

    def test_set_is_initialized(self):
        self.cell.set_is_initialized(True)
        self.assertTrue(self.cell.get_is_initialized())


class TestSudokuPuzzle(unittest.TestCase):
    def setUp(self):
        # 4x4 Puzzle Setup
        self.puzzle_4x4 = SudokuPuzzle(size=4)
        self.correct_values_4x4 = [
            [1, 2, 3, 4],
            [3, 4, 1, 2],
            [4, 1, 2, 3],
            [2, 3, 4, 1]
        ]
        self.puzzle_4x4.set_correct_values(self.correct_values_4x4)

        # # 9x9 Puzzle Setup
        # self.puzzle_9x9 = SudokuPuzzle(size=9)
        # self.correct_values_9x9 = [
        #     [5, 3, None, None, 7, None, None, None, None],
        #     [6, None, None, 1, 9, 5, None, None, None],
        #     [None, 9, 8, None, None, None, None, 6, None],
        #     [8, None, None, None, 6, None, None, None, 3],
        #     [4, None, None, 8, None, 3, None, None, 1],
        #     [7, None, None, None, 2, None, None, None, 6],
        #     [None, 6, None, None, None, None, 2, 8, None],
        #     [None, None, None, 4, 1, 9, None, None, 5],
        #     [None, None, None, None, 8, None, None, 7, 9]
        # ]
        # self.puzzle_9x9.set_correct_values(self.correct_values_9x9)

        self.puzzle_9x9 = SudokuPuzzle(size=9)
        self.correct_values_9x9 = [
            [5, 3, 4, 6, 7, 8, 9, 1, 2],
            [6, 7, 2, 1, 9, 5, 3, 4, 8],
            [1, 9, 8, 3, 4, 2, 5, 6, 7],
            [8, 5, 9, 7, 6, 1, 4, 2, 3],
            [4, 2, 6, 8, 5, 3, 7, 9, 1],
            [7, 1, 3, 9, 2, 4, 8, 5, 6],
            [9, 6, 1, 5, 3, 7, 2, 8, 4],
            [2, 8, 7, 4, 1, 9, 6, 3, 5],
            [3, 4, 5, 2, 8, 6, 1, 7, 9]
        ]
        self.puzzle_9x9.set_correct_values(self.correct_values_9x9)


    # 4x4 Tests
    def test_4x4_initialization(self):
        self.assertEqual(len(self.puzzle_4x4.grid), 4)
        self.assertEqual(len(self.puzzle_4x4.grid[0]), 4)

    def test_4x4_set_correct_values(self):
        for row in range(4):
            for col in range(4):
                cell = self.puzzle_4x4.get_cell(row, col)
                self.assertEqual(cell.get_correct_value(), self.correct_values_4x4[row][col])

    def test_4x4_is_solved(self):
        for row in range(4):
            for col in range(4):
                self.puzzle_4x4.set_inserted_value(row, col, self.correct_values_4x4[row][col])
        self.assertTrue(self.puzzle_4x4.is_solved())

    # 9x9 Tests
    def test_9x9_initialization(self):
        self.assertEqual(len(self.puzzle_9x9.grid), 9)
        self.assertEqual(len(self.puzzle_9x9.grid[0]), 9)

    def test_9x9_set_correct_values(self):
        for row in range(9):
            for col in range(9):
                cell = self.puzzle_9x9.get_cell(row, col)
                self.assertEqual(cell.get_correct_value(), self.correct_values_9x9[row][col])
        # Helper method to fill the grid with correct values (ignoring None values)


    # def test_9x9_is_full(self):
    #     self.assertTrue(self.puzzle_9x9.is_filled())


if __name__ == "__main__":
    unittest.main()
