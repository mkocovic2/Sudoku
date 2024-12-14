"""
Main Contributor : Michael Kocovic, worked on most of routes and functions
Ensured back-end connection and object implementation. Had a hand in 
development in all functions. Connected API routes to database, created document
search for specific boards and id's and worked on main board functionality.

Mintesnot Kassa : Fixed some return errors with the API's, ensured routes were
correctly returning information for the frontend. Developed time saving func with
Michael.

Danny Goldblum: Ensured serialization worked properly, updated history stack
and made it faster. Fixed broken routes and improved speeds. Had a hand in 
the load board, undo move, and undo until correct.
"""
import string
import random
from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
from puzzle_object import SudokuPuzzle
from cell_object import SudokuCell 
from history_stack import HistoryStack
import json
import copy

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# MongoDB Connection
client = MongoClient('mongodb://mongoadmin:teamcMongo@exodus.viewdns.net:27017/')
db = client['sudoku_database']
puzzles_collections = {
    'Easy': db['Easy'],
    'Medium': db['Medium'],
    'Hard': db['Hard']
}
user_sessions_collection = db['UserSessions']

def generate_board_id(length=8):
    """
    Generate a random board ID consisting of uppercase letters and numbers
    """
    characters = string.ascii_uppercase + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def create_sudoku_puzzle_from_grid(grid, size):
    """
    Create a SudokuPuzzle object from a grid and set its correct values
    """
    puzzle = SudokuPuzzle(size=size)
    puzzle.set_correct_values(grid)
    return puzzle

def create_history_stack_from_saved_data(history_data):
    """
    Convert saved history data into a HistoryStack object
    """
    history_stack = HistoryStack()
    
    # If history data exists, recreate the stack
    if history_data:
        for entry in history_data:
            # Use the push method to reconstruct the stack
            history_stack.push(
                entry['action'], 
                entry.get('puzzle_state', None)
            )
    
    return history_stack


def _convert_history_stack(session):
    """
    Convert stored history data to a HistoryStack object
    """
    history_stack = HistoryStack()
    
    # Retrieve history data from the session
    history_data = session.get('history_stack', [])
    
    # Populate the history stack
    for entry in history_data:
        history_stack.push(
            entry['action'], 
            entry.get('puzzle_state', session.get('current_grid_state'))
        )
    
    return history_stack

def _save_history_stack(session_id, history_stack):
    """
    Save HistoryStack to the user session
    """
    # Convert HistoryStack to a storable format
    history_data = [
        {
            'action': entry['action'], 
            'puzzle_state': entry['puzzle_state']
        } for entry in history_stack.stack
    ]
    
    # Update the session with the history data
    user_sessions_collection.update_one(
        {'_id': session_id},
        {
            '$set': {
                'history_stack': history_data,
                'last_updated': datetime.utcnow()
            }
        }
    )

@app.route('/start_puzzle', methods=['POST'])
def start_puzzle():
    data = request.json
    difficulty = data.get('difficulty', 'Easy')
    puzzle_size = data.get('puzzle_size', 9)

    # Query to match the puzzle size
    query = {"size": puzzle_size}

    print(f"Running aggregation with query: {query}")
    
    # Fetch a random puzzle from the selected difficulty
    puzzle_cursor = puzzles_collections[difficulty].aggregate([
        {"$match": query},
        {'$sample': {'size': 1}}
    ])

    # Debug: Print what is returned by the aggregation
    puzzle_list = list(puzzle_cursor)
    print(f"Found puzzles: {puzzle_list}")

    # Check if no documents were returned
    if not puzzle_list:
        return jsonify({'error': 'No puzzle found for the given difficulty and size'}), 404

    puzzle_doc = puzzle_list[0]

    # Check if 'puzzle' exists in the puzzle document
    if 'puzzle' not in puzzle_doc:
        return jsonify({'error': 'Puzzle does not have a grid'}), 400

    # Generate a unique board ID
    board_id = generate_board_id()

    # Create a SudokuPuzzle object to enhance object interaction
    sudoku_puzzle = create_sudoku_puzzle_from_grid(puzzle_doc['puzzle'], puzzle_size)

    # Prepare user session document
    user_session = {
        'board_id': board_id,  # Add board_id for easy retrieval
        'puzzle_id': puzzle_doc['_id'],
        'difficulty': difficulty,
        'puzzle_size': puzzle_size,
        'original_puzzle': puzzle_doc['puzzle'],
        'current_grid_state': puzzle_doc['puzzle'],
        'history_stack': [],
        'start_time': datetime.utcnow(),
        'last_updated': datetime.utcnow(),
        'is_completed': False,
        'time_taken': 0,
        # Add metadata from SudokuPuzzle object
        'puzzle_object_metadata': {
            'is_solved': sudoku_puzzle.is_solved(),
            'is_filled': sudoku_puzzle.is_filled()
        }
    }

    # Insert user session
    session_id = user_sessions_collection.insert_one(user_session).inserted_id

    return jsonify({
        'session_id': str(session_id),
        'board_id': board_id,
        'initial_grid': puzzle_doc['puzzle'],
        # Include additional metadata
        'puzzle_metadata': {
            'is_solved': sudoku_puzzle.is_solved(),
            'is_filled': sudoku_puzzle.is_filled()
        }
    }), 200


@app.route('/load_board', methods=['POST'])
def load_board():
    """ Load a board using its board_id """
    data = request.json
    board_id = data.get('board_id')

    # Find the session with the matching board_id
    session = user_sessions_collection.find_one({'board_id': board_id})
    if not session:
        return jsonify({'error': 'Board not found'}), 404

    return jsonify({
        'session_id': str(session['_id']),
        'board_id': session['board_id'],
        'difficulty': session['difficulty'],
        'puzzle_size': session['puzzle_size'],  # Include puzzle size
        'original_puzzle': session['original_puzzle'],
        'current_grid_state': session['current_grid_state'],
        'time_taken': session.get('time_taken', 0)  # Include the saved time, default to 0 if not set
    }), 200



@app.route('/undo_move', methods=['POST'])
def undo_move():
    """
    Undo the last move in a Sudoku puzzle
    Request body should contain:
    - session_id
    """
    data = request.json
    session_id = ObjectId(data['session_id'])

    # Retrieve user session
    session = user_sessions_collection.find_one({'_id': session_id})
    if not session:
        return jsonify({'error': 'Session not found'}), 404

    # Recreate history stack
    history_stack = _convert_history_stack(session)
    
    # Check if there are moves to undo
    if not history_stack.stack:
        return jsonify({'error': 'No moves to undo'}), 400

    # Retrieve the previous grid state
    last_move = history_stack.pop()
    previous_grid_state = last_move['puzzle_state']
    
    # Update user session
    user_sessions_collection.update_one(
        {'_id': session_id},
        {
            '$set': {
                'current_grid_state': previous_grid_state,
                'last_updated': datetime.utcnow()
            }
        }
    )

    # Save updated history stack
    _save_history_stack(session_id, history_stack)

    return jsonify({
        'success': True, 
        'updated_grid': previous_grid_state,
        'undone_action': last_move['action']
    }), 200

@app.route('/check_solution', methods=['POST'])
def check_solution():
    """
    Check if the current puzzle solution is correct
    Request body should contain:
    - session_id
    """
    data = request.json
    session_id = ObjectId(data['session_id'])

    # Retrieve user session and puzzle
    session = user_sessions_collection.find_one({'_id': session_id})
    if not session:
        return jsonify({'error': 'Session not found'}), 404

    puzzle_doc = puzzles_collections[session['difficulty']].find_one({'_id': session['puzzle_id']})
    
    # Compare current grid with solution
    is_solved = (session['current_grid_state'] == puzzle_doc['solution'])

    if is_solved:
        user_sessions_collection.update_one(
            {'_id': session_id},
            {
                '$set': {
                    'is_completed': True,
                    'time_taken': (datetime.utcnow() - session['start_time']).total_seconds()
                }
            }
        )

    return jsonify({
        'is_solved': is_solved,
        'time_taken': (datetime.utcnow() - session['start_time']).total_seconds() if is_solved else None
    }), 200

@app.route('/undo_until_correct', methods=['POST'])
def undo_until_correct():
    """
    Undo moves starting from the first incorrect move, removing all subsequent moves
    """
    data = request.json
    session_id = ObjectId(data['session_id'])

    # Retrieve user session
    session = user_sessions_collection.find_one({'_id': session_id})
    if not session:
        return jsonify({'error': 'Session not found'}), 404

    # Retrieve the original puzzle solution
    puzzle_doc = puzzles_collections[session['difficulty']].find_one({'_id': session['puzzle_id']})
    solution = puzzle_doc['solution']

    # Recreate history stack
    history_stack = _convert_history_stack(session)

    # If no moves, return current state
    if not history_stack.stack:
        return jsonify({
            'success': True, 
            'updated_grid': session['current_grid_state']
        }), 200

    # Find the first incorrect grid state
    while history_stack.stack:
        # Peek at the last move without removing it
        last_move = history_stack.peek()
        current_grid_state = last_move['puzzle_state']

        # Check if the current grid state is incorrect
        is_incorrect = False
        for i in range(len(current_grid_state)):
            for j in range(len(current_grid_state[i])):
                if current_grid_state[i][j] != solution[i][j]:
                    is_incorrect = True
                    break
            if is_incorrect:
                break

        # If incorrect, pop the move
        if is_incorrect:
            history_stack.pop()
        else:
            # Found the last correct state
            break

    # If all moves were incorrect, reset to original puzzle
    current_grid_state = history_stack.peek()['puzzle_state'] if history_stack.stack else session['original_puzzle']

    # Update user session
    user_sessions_collection.update_one(
        {'_id': session_id},
        {
            '$set': {
                'current_grid_state': current_grid_state,
                'last_updated': datetime.utcnow()
            }
        }
    )

    # Save updated history stack
    _save_history_stack(session_id, history_stack)

    return jsonify({
        'success': True, 
        'updated_grid': current_grid_state
    }), 200

@app.route('/get_hint', methods=['POST'])
def get_hint():
    """
    Provide a hint for the Sudoku puzzle
    Request body should contain:
    - session_id
    - selected_cell (optional): dictionary with 'row' and 'col' keys
    """
    data = request.json
    session_id = ObjectId(data['session_id'])
    selected_cell = data.get('selected_cell')

    # Retrieve user session
    session = user_sessions_collection.find_one({'_id': session_id})
    if not session:
        return jsonify({'error': 'Session not found'}), 404

    # Retrieve the puzzle solution
    puzzle_doc = puzzles_collections[session['difficulty']].find_one({'_id': session['puzzle_id']})
    solution = puzzle_doc['solution']

    # Prepare current grid state
    current_grid = session['current_grid_state']

    # Determine hint cell
    if selected_cell:
        row = selected_cell['row']
        col = selected_cell['col']
        
        # Check if the selected cell is empty or incorrect
        if current_grid[row][col] == 0 or current_grid[row][col] != solution[row][col]:
            current_grid[row][col] = solution[row][col]
            hint_row, hint_col = row, col
        else:
            return jsonify({'error': 'Selected cell is already correct'}), 400
    else:
        # Find empty or incorrect cells
        empty_or_incorrect_cells = [
            (r, c) for r in range(len(current_grid)) 
            for c in range(len(current_grid[r])) 
            if current_grid[r][c] == 0 or current_grid[r][c] != solution[r][c]
        ]

        if not empty_or_incorrect_cells:
            return jsonify({'error': 'No cells available for hint'}), 400

        # Choose a random empty or incorrect cell
        hint_row, hint_col = random.choice(empty_or_incorrect_cells)
        current_grid[hint_row][hint_col] = solution[hint_row][hint_col]

    # Update the user session with the new grid state
    user_sessions_collection.update_one(
        {'_id': session_id},
        {
            '$set': {
                'current_grid_state': current_grid,
                'last_updated': datetime.utcnow()
            },
            '$push': {'history_stack': {
                'action': f'Hint: Set cell ({hint_row}, {hint_col}) to {current_grid[hint_row][hint_col]}',
                'cell_details': {
                    'row': hint_row,
                    'col': hint_col,
                    'previous_value': 0,
                    'new_value': current_grid[hint_row][hint_col]
                }
            }}
        }
    )

    return jsonify({
        'success': True, 
        'hint_row': hint_row, 
        'hint_col': hint_col, 
        'hint_value': current_grid[hint_row][hint_col],
        'updated_grid': current_grid
    }), 200

@app.route('/process_move', methods=['POST'])
def process_move():
    """
    Process a user's move in the Sudoku puzzle and check its correctness
    Using SudokuCell and SudokuPuzzle object methods for validation
    """
    data = request.json
    session_id = ObjectId(data['session_id'])
    row = data['row']
    col = data['col']
    value = data['value']

    # Retrieve user session
    session = user_sessions_collection.find_one({'_id': session_id})
    if not session:
        return jsonify({'error': 'Session not found'}), 404

    # Retrieve the original puzzle solution
    puzzle_doc = puzzles_collections[session['difficulty']].find_one({'_id': session['puzzle_id']})
    solution = puzzle_doc['solution']

    # Recreate history stack
    history_stack = _convert_history_stack(session)

    # Create SudokuPuzzle object to leverage object methods
    sudoku_puzzle = create_sudoku_puzzle_from_grid(session['current_grid_state'], session['puzzle_size'])
    
    # Use SudokuCell to create a cell and set its inserted value
    cell = SudokuCell((row, col), correct_value=solution[row][col])
    cell.set_inserted_value(value)

    # Check correctness using the cell's built-in method
    is_correct = cell.get_is_correct()

    # Update grid state
    current_grid = session['current_grid_state']
    previous_value = current_grid[row][col]
    current_grid[row][col] = value

    # Push the move to history stack
    history_stack.push(
        f'Set cell ({row}, {col}) to {value}', 
        copy.deepcopy(current_grid)
    )

    # Update user session
    user_sessions_collection.update_one(
        {'_id': session_id},
        {
            '$set': {
                'current_grid_state': current_grid,
                'last_updated': datetime.utcnow(),
                'puzzle_object_metadata': {
                    'is_solved': sudoku_puzzle.is_solved(),
                    'is_filled': sudoku_puzzle.is_filled()
                }
            }
        }
    )

    # Save history stack
    _save_history_stack(session_id, history_stack)

    return jsonify({
        'success': True, 
        'is_correct': is_correct,
        'correct_value': solution[row][col],
        'updated_grid': current_grid,
        'puzzle_metadata': {
            'is_solved': sudoku_puzzle.is_solved(),
            'is_filled': sudoku_puzzle.is_filled()
        }
    }), 200

@app.route('/save_time', methods=['POST'])
def save_time():
    data = request.json
    board_id = data.get('board_id')
    time_taken = data.get('time_taken')  # Time taken in seconds

    if not board_id or time_taken is None:
        return jsonify({'error': 'Missing board_id or time_taken'}), 400

    # Find the session with the matching board_id
    session = user_sessions_collection.find_one({'board_id': board_id})
    if not session:
        return jsonify({'error': 'Board not found'}), 404

    # Update the session with the time_taken and set the puzzle as completed
    update_result = user_sessions_collection.update_one(
        {'board_id': board_id},
        {'$set': {
            'time_taken': time_taken,
            'is_completed': True,
            'last_updated': datetime.utcnow()  # Update the last updated timestamp
        }}
    )

    if update_result.matched_count == 0:
        return jsonify({'error': 'Failed to update the session'}), 500

    return jsonify({'message': 'Time saved successfully', 'time_taken': time_taken}), 200

@app.route('/store_incorrect_moves', methods=['POST'])
def store_incorrect_moves():
    """
    Check the current board for incorrect moves and return them.
    Request body should contain:
    - session_id
    """
    data = request.json
    session_id = ObjectId(data['session_id'])

    # Retrieve user session
    session = user_sessions_collection.find_one({'_id': session_id})
    if not session:
        return jsonify({'error': 'Session not found'}), 404

    # Retrieve the original puzzle solution
    puzzle_doc = puzzles_collections[session['difficulty']].find_one({'_id': session['puzzle_id']})
    solution = puzzle_doc['solution']

    # Get the current board state
    current_grid = session['current_grid_state']

    # Create a map to store the incorrect moves
    wrong_moves = {}

    # Compare the current grid with the solution
    for i in range(session['puzzle_size']):
        for j in range(session['puzzle_size']):
            if current_grid[i][j] != solution[i][j]:
                # Store the incorrect move with its coordinates
                wrong_moves[json.dumps([i, j])] = [i, j]

    return jsonify({
        'wrong_moves': wrong_moves
    }), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4655)
