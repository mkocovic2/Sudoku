import { Component, ElementRef, HostListener, OnInit, ViewChild } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
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
    private apiService: ApiService,
    private router: Router, 
  ){}

  Math = Math
  boxes: any[] = []
  board: number[][] = [];
  puzzleSolution: number[][] = []
  preDefined: number[][] = []
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
  boardId: string = ''
  pauseSize: number = 38
  startTime: number = -1

  @HostListener('window:beforeunload', ['$event'])
  onWindowReload(event: BeforeUnloadEvent): void {
    this.updateTime()
  }

  ngOnInit(): void {
    this.route.queryParams.subscribe((params) => {
      this.difficulty = params['difficulty'] || null;
      this.size = params['size'] || null;
      this.boardId = params['boardId'] || null;
      this.boxes = Array.from({ length: this.size }).fill(0)
      this.board = Array.from({ length: this.size }, () => Array(this.size).fill(0))
      this.puzzleSolution = Array.from({ length: this.size }, () => Array(this.size).fill(0))
      this.preDefined = Array.from({ length: this.size }, () => Array(this.size).fill(0))
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
          this.board = JSON.parse(JSON.stringify(res?.board))
          this.puzzleSolution = JSON.parse(JSON.stringify(res?.board))
          this.preDefined = JSON.parse(JSON.stringify(res?.preDefined))
          this.session_id = res?.session_id,
          this.startTime = res?.time_taken
        } else {
          this.apiService.loadBoard({board_id: this.boardId}).subscribe({
            next: (res: any) => {
                this.board = JSON.parse(JSON.stringify(res?.current_grid_state))
                this.puzzleSolution = JSON.parse(JSON.stringify(res?.current_grid_state))
                this.preDefined = JSON.parse(JSON.stringify(res?.original_puzzle))
                this.session_id = res?.session_id
                this.startTime = res?.time_taken
                setTimeout(() => {this.startTime = res?.time_taken}, 100)
            }
          })
        }
      }
    }) 
  }

  backToMenu() {
    this.updateTime()
  }

  makeMove(x:number, y:number, value:number) {
    const move = {
      session_id: this.session_id,
      row: x,
      col: y,
      value: value + 1
    }
    this.apiService.makeMove(move).subscribe({
      next: (res: any) => {
        const {correct_value} = res
        this.puzzleSolution[x][y] = correct_value
      }
    })
  }

  setCell(value: any) {
    // if (typeof(value) == number) value = value
    // if (typeof(value) == KeyboardEvent) {
    //   value = value.key
    // }
    this.action = ''
    const [x, y] = this.getPosition()
    
    if (x == -1 || y == -1) return

    if (this.noteMode) {
      //take note
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
      //set cell value
      if (this.preDefined[x][y] == 0 || this.preDefined[x][y] == null) {
        this.board[x][y] = value + 1
      }
    this.setPosition(-1,-1)
    this.makeMove(x, y, value)  
    } 
  }

  getPosition() {
    return this.clickedBoxPosition
  }

  setPosition(row: number, col: number) {
    this.clickedBoxPosition = [row, col]
  }

  undoAll() {
    this.apiService.undoUntilCorrect({session_id: this.session_id}).subscribe({
      next: (res: any) => {
        if (res?.success) this.board = res?.updated_grid
      }
    })
  }

  undoLast() {
    this.apiService.undoMove({session_id: this.session_id}).subscribe({
      next: (res: any) => {
        if (res?.success) this.board = res?.updated_grid
      }
    })
  }

  isCompeleted():boolean {
    for(let i=0; i<this.size; i++){
      for(let j=0; j<this.size; j++){
        if (this.board[i][j] == 0 || this.board[i][j] == null) return false
      }
    }
    return true
  }

  check() {
    const isCompeleted: boolean = this.isCompeleted()
    if (isCompeleted) {
      this.apiService.checkSolution({session_id: this.session_id}).subscribe({
        next: (res: any) => {
          if (res?.is_solved) {
            this.router.navigate(['/congradulation'])
          } else {
            console.log('Try Again!!!')
          }
        }
      })
    }
  }

  hint(row: number, col: number) {
    this.apiService.getHint({
      session_id: this.session_id,
      selected_cell: row && row > -1 ? {row: row,col: col} : {}
    }).subscribe({
      next: (res: any) => {
        this.hintRow = res?.hint_row
        this.hintCol = res?.hint_col
        this.board[this.hintRow][this.hintCol] = res?.hint_value
        setTimeout(() => {
          this.hintRow = -1
          this.hintCol = -1
          this.setPosition(-1,-1)
        }, 1000)
      }
    })
  }

  setAction(action: string) {
    this.action = action
    if (action == 'UNDO LAST') {
      this.undoLast()
    }
    if (action == 'UNDO ALL') {
      this.undoAll()
    }
    if (action == 'CHECK') {
      this.check()
    }
    if (action == 'HINT') {
      const [row, col] = this.clickedBoxPosition
      this.hint(row, col)
    }
    if (action == 'NOTE') {
      this.noteMode = !this.noteMode
      if (!this.noteMode) {
        this.action = ''
      }
    }
  }

  updateTime() {
    const {hours, minutes, seconds} = this.time.get()
    const totalTime = hours*3600 + minutes*60 + seconds
    this.apiService.updateTime({
      board_id: this.boardId,
      time_taken: totalTime
    });
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
