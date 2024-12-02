from pymongo import MongoClient
import copy

# Connect to MongoDB
client = MongoClient(
    'mongodb://mongoadmin:teamcMongo@exodus.viewdns.net:27017/')
# replace 'your_database_name' with your actual database name
db = client['sudoku_database']

# List of collections to iterate through
collections = ['Easy', 'Medium', 'Hard']


def is_valid(board, row, col, num):
    """Check if placing num at board[row][col] is valid according to Sudoku rules."""
    # Check row
    if num in board[row]:
        return False
    # Check column
    if num in [board[r][col] for r in range(9)]:
        return False
    # Check 3x3 subgrid
    start_row, start_col = 3 * (row // 3), 3 * (col // 3)
    for i in range(3):
        for j in range(3):
            if board[start_row + i][start_col + j] == num:
                return False
    return True


def solve_sudoku(board):
    """Solve the Sudoku puzzle using backtracking."""
    for row in range(9):
        for col in range(9):
            if board[row][col] == 0:  # Find an empty cell
                for num in range(1, 10):  # Try numbers 1 to 9
                    if is_valid(board, row, col, num):
                        board[row][col] = num
                        if solve_sudoku(board):
                            return True
                        board[row][col] = 0  # Reset on backtrack
                return False  # No valid number found, trigger backtracking
    return True  # Puzzle solved


def solve_and_update(collection):
    """Fetch puzzles, solve them, and update the solution field."""
    puzzles = db[collection].find({"solution": None})  # Get unsolved puzzles
    for puzzle in puzzles:
        puzzle_id = puzzle['_id']
        sudoku_board = puzzle['puzzle']
        # Copy the puzzle to solve it
        solution_board = copy.deepcopy(sudoku_board)

        if solve_sudoku(solution_board):
            # Update the solution in the database
            db[collection].update_one(
                {"_id": puzzle_id},
                {"$set": {"solution": solution_board}}
            )
            print(
                f"Solved and updated puzzle in '{collection}' with _id: {puzzle_id}")
        else:
            print(
                f"Could not solve puzzle in '{collection}' with _id: {puzzle_id}")


# Iterate through each collection and solve puzzles
for collection in collections:
    solve_and_update(collection)

print("All puzzles processed.")
