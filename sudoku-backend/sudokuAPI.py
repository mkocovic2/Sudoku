import string
import random
from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
from puzzle_object import SudokuPuzzle  # Your existing Sudoku class

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

    # Prepare user session document
    user_session = {
        'board_id': board_id,  # Add board_id for easy retrieval
        'puzzle_id': puzzle_doc['_id'],
        'difficulty': difficulty,
        'puzzle_size': puzzle_size,
        'current_grid_state': puzzle_doc['puzzle'],
        'history_stack': [],
        'start_time': datetime.utcnow(),
        'last_updated': datetime.utcnow(),
        'is_completed': False,
        'time_taken': 0
    }

    # Insert user session
    session_id = user_sessions_collection.insert_one(user_session).inserted_id

    return jsonify({
        'session_id': str(session_id),
        'board_id': board_id,
        'initial_grid': puzzle_doc['puzzle']
    }), 200


@app.route('/load_board', methods=['POST'])
def load_board():
    """
    Load a board using its board_id
    """
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
        'current_grid_state': session['current_grid_state']
    }), 200


@app.route('/make_move', methods=['POST'])
def make_move():
    """
    Process a user's move in the Sudoku puzzle
    Request body should contain:
    - session_id
    - row
    - col
    - value
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

    # Update grid state and history
    current_grid = session['current_grid_state']
    
    # Store previous value for undo functionality
    previous_value = current_grid[row][col]
    current_grid[row][col] = value

    # Push to history stack
    history_entry = {
        'action': f'Set cell ({row}, {col}) to {value}',
        'cell_details': {
            'row': row,
            'col': col,
            'previous_value': previous_value,
            'new_value': value
        }
    }

    user_sessions_collection.update_one(
        {'_id': session_id},
        {
            '$set': {
                'current_grid_state': current_grid,
                'last_updated': datetime.utcnow()
            },
            '$push': {'history_stack': history_entry}
        }
    )

    return jsonify({'success': True, 'updated_grid': current_grid}), 200

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

    # Pop last history entry
    if session['history_stack']:
        last_move = session['history_stack'].pop()
        
        # Retrieve the cell details
        row = last_move['cell_details']['row']
        col = last_move['cell_details']['col']
        previous_value = last_move['cell_details']['previous_value']
        
        # Get current grid state
        current_grid = session['current_grid_state']
        
        # Revert the cell to its previous value
        current_grid[row][col] = previous_value
        
        user_sessions_collection.update_one(
            {'_id': session_id},
            {
                '$set': {
                    'current_grid_state': current_grid,
                    'history_stack': session['history_stack'],
                    'last_updated': datetime.utcnow()
                }
            }
        )

        return jsonify({
            'success': True, 
            'updated_grid': current_grid
        }), 200
    else:
        return jsonify({'error': 'No moves to undo'}), 400

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
    Undo moves until the board is in a correct state
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

    # Create a copy of the current grid to modify
    current_grid = session['current_grid_state']
    history_stack = session['history_stack']

    # Undo moves until the board matches the solution up to the current point
    while history_stack:
        # Get the last move
        last_move = history_stack.pop()
        
        # Revert the specific cell
        row = last_move['cell_details']['row']
        col = last_move['cell_details']['col']
        previous_value = last_move['cell_details']['previous_value']
        
        # Check if this move was incorrect
        if current_grid[row][col] != solution[row][col]:
            # Revert the cell
            current_grid[row][col] = previous_value
        else:
            # If we've reached a correct configuration, put the move back and stop
            history_stack.append(last_move)
            break

    # Update the user session
    user_sessions_collection.update_one(
        {'_id': session_id},
        {
            '$set': {
                'current_grid_state': current_grid,
                'history_stack': history_stack,
                'last_updated': datetime.utcnow()
            }
        }
    )

    return jsonify({
        'success': True, 
        'updated_grid': current_grid
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

@app.route('/check_cell_correctness', methods=['POST'])
def check_cell_correctness():
    data = request.json
    session_id = ObjectId(data['session_id'])
    row = data['row']
    col = data['col']
    value = data['value']

    # Retrieve user session and puzzle
    session = user_sessions_collection.find_one({'_id': session_id})
    if not session:
        return jsonify({'error': 'Session not found'}), 404

    # Retrieve the original puzzle solution
    puzzle_doc = puzzles_collections[session['difficulty']].find_one({'_id': session['puzzle_id']})
    solution = puzzle_doc['solution']

    # Check if the entered value matches the solution
    is_correct = (solution[row][col] == value)

    return jsonify({
        'is_correct': is_correct,
        'correct_value': solution[row][col]
    }), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4655)