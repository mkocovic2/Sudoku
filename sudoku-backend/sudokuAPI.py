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

@app.route('/start_puzzle', methods=['POST'])
def start_puzzle():
    data = request.json
    user_id = ObjectId(data.get('user_id'))
    difficulty = data.get('difficulty', 'Easy')
    puzzle_size = data.get('puzzle_size', 9)

    # Fetch a random puzzle from the selected difficulty
    puzzle_doc = puzzles_collections[difficulty].aggregate([
        {'$sample': {'size': 1}}
    ]).next()

    # Check if 'puzzle' exists in the puzzle document
    if 'puzzle' not in puzzle_doc:
        return jsonify({'error': 'Puzzle does not have a grid'}), 400

    # Create SudokuPuzzle instance
    puzzle = SudokuPuzzle(size=puzzle_size)
    puzzle.set_correct_values(puzzle_doc['solution'])

    # Prepare user session document
    user_session = {
        'user_id': user_id,
        'puzzle_id': puzzle_doc['_id'],
        'difficulty': difficulty,
        'puzzle_size': puzzle_size,
        'current_grid_state': [[None for _ in range(puzzle_size)] for _ in range(puzzle_size)],
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
        'initial_grid': puzzle_doc['puzzle']  # Updated field name
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
    current_grid[row][col] = value

    # Push to history stack
    history_entry = {
        'action': f'Set cell ({row}, {col}) to {value}',
        'puzzle_state': current_grid
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
        last_state = session['history_stack'].pop()
        
        user_sessions_collection.update_one(
            {'_id': session_id},
            {
                '$set': {
                    'current_grid_state': last_state['puzzle_state'],
                    'history_stack': session['history_stack'],
                    'last_updated': datetime.utcnow()
                }
            }
        )

        return jsonify({
            'success': True, 
            'updated_grid': last_state['puzzle_state']
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4655)
