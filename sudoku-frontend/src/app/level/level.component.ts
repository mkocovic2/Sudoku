import { Component } from '@angular/core';
import { ApiService } from '../services/api.service';
import { Router } from '@angular/router';
import { take } from 'rxjs';

@Component({
  selector: 'app-level',
  templateUrl: './level.component.html',
  styleUrls: ['./level.component.scss']
})
export class LevelComponent {

  constructor(
    private router: Router, 
    private apiService: ApiService
  ) {}

  difficulty: string = ''
  size: number = 0
  boardId: string = ''

  //Call api to fetch new game board with the selected size and difficulty 
  startPuzzle() {
      const game = { 
        difficulty: this.difficulty,
        puzzle_size: this.size,
        user_id: this.generateUserId() 
      }
      this.apiService.startPuzzle(game).pipe(take(1)).subscribe({
        next: (res: any) => {
          if (Object.keys(res).length > 0) {
            //Fill the observer with board data to be subscribed in game board page
            this.apiService.updateBoard({board: res?.initial_grid, preDefined: res?.initial_grid, session_id: res?.session_id, time_taken: 0})
            //Navigate to the game board page with the boardId included as query params
            this.router.navigate(['/board'], {
              queryParams: {difficulty: this.difficulty, size: this.size, boardId: res?.board_id}
            })
          }
        }
      })
  }

  //Call api to continue a game
  loadBoard() {
    this.apiService.loadBoard({board_id: this.boardId}).subscribe({
      next: (res: any) => {
        {
          //Fill the observer with board data to be subscribed in game board page
          this.apiService.updateBoard({board: res?.current_grid_state, preDefined: res?.original_puzzle, session_id: res?.session_id, time_taken: res?.time_taken})
          //Navigate to the game board page with the boardId included as query params
          this.router.navigate(['/board'], {
            queryParams: {difficulty: res?.difficulty, size: res?.puzzle_size, boardId: res?.board_id}
          })
      }
      }
    })
  }

  //Generate random Id for the user
  generateUserId() {
    return Math.random().toString(36).substr(2, 9);
  }

  //Select size of sudoku game
  selectSize(size: number) {
    this.size = size
  }

  //Select difficulty of sudoku game
  selectDifficulty(difficulty: string) {
    this.difficulty = difficulty
  }
}
