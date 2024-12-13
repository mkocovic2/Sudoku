# Sudoku Solver App  

### **Contributors**
#### Mintesnot Kassa
  Primarily worked on Front-end responsiveness and architecture. Contributed to API decisions and functions by fixing routing errors and incorrect returns. Helped the team with creating the skeleton for the test-frontend for easier integration. 
Created a majority of the JS functions for routes in the front-end, and ensured responsive design for mobile devices.
#### Danny Goldblum
  Primarily worked on the object design and API for the back-end. Expanded the test front-end for more visual support, and worked on some the puzzle generation and solving algorithms. Main contributer to the object files and helped with API function routing. Created test routes on the API, and later integrated with some of the object files. Worked on the some of basic UI buttons on the front-end.
#### Michael Kocovic  
  Primarily worked on API and database integrations. Created initial database schema in MongoDB, and contributed to the overall model of the API. Created JS functions and buttons for each route in the test-frontend, and later integrated some of the buttons into the main frontend. Built a majority of the routes for API integrations, and made some tweaks to the object files. 

## **Overview**  
This project is a feature-rich Sudoku solving app designed to provide an engaging and customizable experience for users of all skill levels. The application supports multiple puzzle sizes, difficulties, and dynamic interaction features to enhance problem-solving.

---

## **Features**  

1. **Puzzle Sizes**  
   - Supports puzzles of various dimensions:  
     - 9x9 (standard)  
     - 4x4 (beginner)  
     - 16x16 (advanced)  

2. **Puzzle Selection**  
   - Choose from a library of pre-generated puzzles.  
   - Generate puzzles on-demand for a fresh challenge.  

3. **Difficulty Levels**  
   - Puzzles categorized into difficulty levels: Easy, Medium, and Hard.  

4. **Interactive Gameplay**  
   - Make **notations** in cells to track possible numbers.  
   - **Check solution progress** to validate completed sections.  
   - **Undo**:  
     - Undo the last move.  
     - Undo all incorrect moves.  

5. **Hints**  
   - Get a **random hint** to progress in the puzzle.  
   - Request a **specific hint** for targeted assistance.  

6. **Timer**  
   - Track the time taken to solve the puzzle for competitive play or personal improvement.

---

## **Sudoku Rules**  

1. **Basic Rules**  
   - Each row must contain all unique numbers without repetition.  
   - Each column must contain all unique numbers without repetition.  
   - Each grid section (e.g., 3x3 in a 9x9 puzzle) must also contain all unique numbers without repetition.  

2. **Placement Rules**  
   - Numbers can only be placed in empty cells.  
   - Players cannot overwrite pre-filled cells.  

3. **Hints and Notes**  
   - Notes are temporary markings to track potential numbers for a cell.  
   - Hints provide a valid number for a specific cell but may impact your completion time.  

4. **Puzzle Completion**  
   - A puzzle is considered solved when all cells are correctly filled according to the rules.  
   - Players can check progress to identify mistakes and revise their solution.  

---
