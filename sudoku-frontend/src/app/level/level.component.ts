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

  startPuzzle() {
      const game = { 
        difficulty: this.difficulty,
        puzzle_size: this.size,
        user_id: this.generateUserId() 
      }
      this.apiService.startPuzzle(game).pipe(take(1)).subscribe({
        next: (res: any) => {
          if (Object.keys(res).length > 0) {
            this.apiService.updateBoard({board: res?.initial_grid, session_id: res?.session_id})
            this.router.navigate(['/board'], {
              queryParams: {difficulty: this.difficulty, size: this.size, user: game.user_id}
            })
          }
        }
      })
  }

  generateUserId() {
    return Math.random().toString(36).substr(2, 9);
  }

  selectSize(size: number) {
    this.size = size
  }

  selectDifficulty(difficulty: string) {
    this.difficulty = difficulty
  }
}
