from pymongo import MongoClient
import copy

# Connect to MongoDB
client = MongoClient(
    'mongodb://mongoadmin:teamcMongo@exodus.viewdns.net:27017/')
# Replace 'your_database_name' with your actual database name
db = client['sudoku_database']

# List of collections to iterate through
collections = ['Easy', 'Medium', 'Hard']


def is_valid(board, row, col, num):
    """Check if placing num at board[row][col] is valid according to Sudoku rules."""
    # Check row
    if num in board[row]:
        return False
    # Check column
    if num in [board[r][col] for r in range(len(board))]:
        return False
    # Check subgrid
    size = int(len(board)**0.5)  # Assuming the board is a square (e.g., 9x9 or 4x4)
    start_row, start_col = size * (row // size), size * (col // size)
    for i in range(size):
        for j in range(size):
            if board[start_row + i][start_col + j] == num:
                return False
    return True


def solve_sudoku(board):
    """Solve the Sudoku puzzle using backtracking."""
    for row in range(len(board)):
        for col in range(len(board)):
            if board[row][col] == 0:  # Find an empty cell
                for num in range(1, len(board) + 1):  # Try numbers 1 to size
                    if is_valid(board, row, col, num):
                        board[row][col] = num
                        if solve_sudoku(board):  # If solution found, return True
                            return True
                        board[row][col] = 0  # Reset on backtrack
                return False  # No valid number found, trigger backtracking
    return True  # Puzzle solved


def solve_and_update(collection):
    """Fetch puzzles, solve them, and update the solution and size fields."""
    puzzles = db[collection].find({"solution": {"$exists": False}})  # Get puzzles without a solution field
    for puzzle in puzzles:
        puzzle_id = puzzle['_id']
        sudoku_board = puzzle.get('puzzle')  # Safely retrieve 'puzzle', or default to None

        if sudoku_board is None:
            # Initialize with an empty puzzle if 'puzzle' is missing
            size = 9  # Default size
            sudoku_board = [[0] * size for _ in range(size)]
            db[collection].update_one(
                {"_id": puzzle_id},
                {"$set": {"puzzle": sudoku_board, "size": size}}
            )
            print(
                f"Initialized missing puzzle in '{collection}' with _id: {puzzle_id}, size: {size}")

        # Solve the puzzle
        solution_board = copy.deepcopy(sudoku_board)

        if solve_sudoku(solution_board):
            size = len(sudoku_board)  # Determine size of the puzzle
            # Update the solution and size in the database
            db[collection].update_one(
                {"_id": puzzle_id},
                {"$set": {"solution": solution_board, "size": size}}
            )
            print(
                f"Solved and updated puzzle in '{collection}' with _id: {puzzle_id}, size: {size}")
        else:
            print(
                f"Could not solve puzzle in '{collection}' with _id: {puzzle_id}")


# Iterate through each collection and solve puzzles
for collection in collections:
    solve_and_update(collection)

print("All puzzles processed.")
