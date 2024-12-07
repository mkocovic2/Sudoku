import { Component, ElementRef, OnInit, ViewChild } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { take } from 'rxjs';
import { ApiService } from '../services/api.service';

@Component({
  selector: 'app-board',
  templateUrl: './board.component.html',
  styleUrls: ['./board.component.scss']
})
export class BoardComponent implements OnInit {
  constructor(
    private route: ActivatedRoute,
    private apiService: ApiService
  ){}

  boxes = Array(9)
  board: number[][] = Array.from({ length: 9 }, () => Array(9).fill(0));
  puzzleSolution: number[][] = Array.from({length: 9}, () => Array(9).fill(0))
  clickedBoxPosition: number[] = [-1, -1]
  noteMode: boolean = false
  action: string = ''
  noteBoxes = Array(3)
  noteBoard = Array.from({ length: 9 }, () => 
    Array.from({ length: 9 }, () => 
        Array.from({ length: 3 }, () => 
            Array(3).fill(0)
        )
    )
  );
  @ViewChild('time', { static: false }) time!: any;
  isTimePaused: boolean = false
  difficulty: string = ''
  session_id: string = ''

  ngOnInit(): void {
    this.route.queryParams.subscribe((params) => {
      this.difficulty = params['difficulty'] || null;
    });
    this.apiService.boardObs.subscribe({
      next: (res) => {
        if (Object.keys(res).length > 0) {
          this.board = res?.board
          this.session_id = res?.session_id
        }
      }
    }) 
  }

  selectCell(i:number, j:number) {
    this.clickedBoxPosition = [i, j]
  }

  setCell(value: number) {
    this.action = ''
    const [x, y] = this.getPosition()
    
    if (x == -1 || y == -1) return

    if (this.noteMode) {
      const n = Math.floor(value/3)
      const m = value%3
      if (this.board[x][y] == 0) {
        if (this.noteBoard[x][y][n][m] == 0) {
          this.noteBoard[x][y][n][m] = value + 1
        } else {
          this.noteBoard[x][y][n][m] = 0
        }
      }
    }
    else {
      if (this.board[x][y] == 0) {
        this.board[x][y] = value + 1
      }
      const move = {
					session_id: this.session_id,
					row: x,
					col: y,
					value: value + 1
      }
      this.apiService.makeMove(move).subscribe()
    } 
  }

  getPosition() {
    return this.clickedBoxPosition
  }

  setAction(action: string) {
    if (action == 'UNDO') {
      this.action = action
      this.apiService.undoMove({session_id: this.session_id}).subscribe({
        next: (res: any) => {
          if (res?.success) this.board = res?.updated_grid
        }
      })
    }
    if (action == 'NOTE') {
      this.noteMode = !this.noteMode
    }
    if (action == 'CHECK') {
      this.action = action
    }
  }

  filterWrongMoves() {
    const wrongMoves = new Map();
    for(let i=0; i<9; i++) {
      for(let j=0; j<9; j++) {
        if(this.puzzleSolution[i][j] != this.board[i][j]) {
          wrongMoves.set(JSON.stringify([i,j]), [i,j])
        }
      }
    }

    return wrongMoves
  }

  compareWithSolution(i: number, j: number) {
    const wrongMoves = this.filterWrongMoves()
    if (wrongMoves.has(JSON.stringify([i,j]))) {
      return true
    }
    return false
  }

  checkPuzzle(i: number, j: number) {
    if (this.action == 'CHECK' && this.compareWithSolution(i,j)) {
      return true
    }
    return false
  }

  handleTime() {
    this.isTimePaused = !this.isTimePaused
    if (this.isTimePaused){
      this.time.stop()
    } else {
      this.time.resume()
    }
  }

  clearNote(x: number, y: number ) {
    if (this.board[x][y] > 0) {
      return false
    }
    return true
  }
}
