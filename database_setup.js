//  Done by Danny Goldblum - Depricated //


const { MongoClient } = require('mongodb');

// MongoDB connection URI (replace with your URI if needed)
const uri = "mongodb://mongoadmin:teamcMongo@exodus.viewdns.net:27017/";

// Create a new MongoClient
const client = new MongoClient(uri);

async function setupDatabase() {
  try {
    // Connect to MongoDB
    await client.connect();

    // Select the database
    const db = client.db('sudoku_database');

    // Collections for the schema
    const difficultyCollection = db.collection('Difficulty');
    const sizeCollection = db.collection('PuzzleSize');
    const usersCollection = db.collection('Users');
    const puzzleCollection = db.collection('SudokuPuzzle');
    const userSessionCollection = db.collection('UserSessions');

    console.log('Database setup complete');
  } finally {
    // Close the connection
    await client.close();
  }
}

// Run the database setup
setupDatabase().catch(console.dir);
