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

  Math = Math
  boxes: any[] = []
  board: number[][] = [];
  puzzleSolution: number[][] = Array.from({length: 9}, () => Array(9).fill(0))
  clickedBoxPosition: number[] = [-1, -1]
  noteMode: boolean = false
  action: string = ''
  noteBoxes: any[] = []
  noteBoard: number[][][][] = []
  @ViewChild('time', { static: false }) time!: any;
  isTimePaused: boolean = false
  difficulty: string = ''
  session_id: string = ''
  size: number = 0
  hintRow: number = -1
  hintCol: number = -1

  ngOnInit(): void {
    this.route.queryParams.subscribe((params) => {
      this.difficulty = params['difficulty'] || null;
      this.size = params['size'] || null;
      this.boxes = Array.from({ length: this.size }).fill(0)
      this.board = Array.from({ length: this.size }, () => Array(this.size).fill(0))
      this.noteBoxes = Array.from({ length: this.Math.sqrt(this.size) }).fill(0)
      this.noteBoard = Array.from({ length: this.size }, () => 
        Array.from({ length: this.size }, () => 
            Array.from({ length: Math.sqrt(this.size) }, () => 
                Array(Math.sqrt(this.size)).fill(0)
            )
        )
      );
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

  setCell(value: number) {
    this.action = ''
    const [x, y] = this.getPosition()
    
    if (x == -1 || y == -1) return

    if (this.noteMode) {
      const n = Math.floor(value/Math.sqrt(this.size))
      const m = value%Math.sqrt(this.size)
      if (this.board[x][y] == 0 || this.board[x][y] == null) {
        if (this.noteBoard[x][y][n][m] == 0 || this.noteBoard[x][y][n][m] == null) {
          this.noteBoard[x][y][n][m] = value + 1
        } else {
          this.noteBoard[x][y][n][m] = 0
        }
      }
    }
    else {
      if (this.board[x][y] == 0 || this.board[x][y] == null) {
        this.board[x][y] = value + 1
      }
    this.setPosition(-1,-1)
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

  setPosition(row: number, col: number) {
    this.clickedBoxPosition = [row, col]
  }

  undo() {
    this.apiService.undoMove({session_id: this.session_id}).subscribe({
      next: (res: any) => {
        if (res?.success) this.board = res?.updated_grid
      }
    })
  }

  hint(row: number, col: number) {
    this.apiService.getHint({
      session_id: this.session_id,
      select_cell: {
        row: row,
        col: col
      }
    }).subscribe({
      next: (res: any) => {
        this.hintRow = res?.hint_row
        this.hintCol = res?.hint_col
        this.board[this.hintRow][this.hintCol] = res?.hint_value
        setTimeout(() => {
          this.hintRow = -1
          this.hintCol = -1
        }, 1000)
      }
    })
  }

  setAction(action: string) {
    this.action = action
    if (action == 'UNDO') {
      this.undo()
    }

    if (action == 'CHECK') {
    }
    if (action == 'HINT') {
      const [row, col] = this.clickedBoxPosition
      this.hint(row, col)
    }
    if (action == 'NOTE') {
      this.noteMode = !this.noteMode
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
