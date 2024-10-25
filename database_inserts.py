from pymongo import MongoClient
from datetime import datetime

client = MongoClient("mongodb://mongoadmin:teamcMongo@exodus.viewdns.net:27017/")
db = client['sudoku_database']


def get_difficulty_id(difficulty_name):
    return db.Difficulty.find_one({"difficulty_name": difficulty_name})["_id"]

def get_size_id(size_name):
    return db.PuzzleSize.find_one({"size_name": size_name})["_id"]

db.SudokuPuzzle.insert_many([
    {
        "difficulty_id": get_difficulty_id("Easy"),
        "size_id": get_size_id("4x4"),
        "puzzle_data": "sample_puzzle_data_easy_4x4" #Change this
    },
    {
        "difficulty_id": get_difficulty_id("Medium"),
        "size_id": get_size_id("4x4"),
        "puzzle_data": "sample_puzzle_data_medium_4x4" #Change this
    },
    {
        "difficulty_id": get_difficulty_id("Hard"),
        "size_id": get_size_id("4x4"),
        "puzzle_data": "sample_puzzle_data_hard_4x4" #Change this
    },
    {
        "difficulty_id": get_difficulty_id("Easy"),
        "size_id": get_size_id("9x9"),
        "puzzle_data": "sample_puzzle_data_easy_9x9" #Change this
    },
    {
        "difficulty_id": get_difficulty_id("Medium"),
        "size_id": get_size_id("9x9"),
        "puzzle_data": "sample_puzzle_data_medium_9x9" #Change this
    },
    {
        "difficulty_id": get_difficulty_id("Hard"),
        "size_id": get_size_id("9x9"),
        "puzzle_data": "sample_puzzle_data_hard_9x9" #Change this
    }
])

# Create UserSessions collection and track sessions
def get_user_id(username):
    return db.Users.find_one({"username": username})["_id"]

def get_puzzle_id(puzzle_data):
    return db.SudokuPuzzle.find_one({"puzzle_data": puzzle_data})["_id"]

# Add a session for User1
db.UserSessions.insert_one({
    "user_id": get_user_id("User1"),
    "puzzle_id": get_puzzle_id("sample_puzzle_data_easy_4x4"),
    "size_id": get_size_id("4x4"),
    "start_time": datetime.now()
})

# Add another session for User2
db.UserSessions.insert_one({
    "user_id": get_user_id("User2"),
    "puzzle_id": get_puzzle_id("sample_puzzle_data_medium_9x9"),
    "size_id": get_size_id("9x9"),
    "start_time": datetime.now()
})

print("Data insertion complete.")