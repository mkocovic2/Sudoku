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
  wrongMoves: boolean[][] = []
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
  fourByFour: number = 64
  nineByNine: number = 32

  //update game time on hard reload or exit from game
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
      this.wrongMoves = Array.from({ length: this.size }, () => Array.from({length: this.size}, () => false))
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
          this.wrongMoves = Array.from({ length: this.size }, () => Array.from({length: this.size}, () => false))
          this.session_id = res?.session_id,
          this.startTime = res?.time_taken
        } else {
          this.apiService.loadBoard({board_id: this.boardId}).subscribe({
            next: (res: any) => {
                this.board = JSON.parse(JSON.stringify(res?.current_grid_state))
                this.puzzleSolution = JSON.parse(JSON.stringify(res?.current_grid_state))
                this.preDefined = JSON.parse(JSON.stringify(res?.original_puzzle))
                this.wrongMoves = Array.from({ length: this.size }, () => Array.from({length: this.size}, () => false))
                this.session_id = res?.session_id
                this.startTime = res?.time_taken
            }
          })
        }
      }
    }) 
  }

  //Update game time on navigation to main page
  backToMenu() {
    this.updateTime()
  }

  //Update the move on the selected cell to backend
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

  //Update value of specific cell
  //Update value of note on specific cell if action is 'Note' or if noteMode == True
  setCell(value: any) {
    this.action = ''
    const [x, y] = this.getPosition()
    //Cell is not selected
    if (x == -1 || y == -1) return
    //Update note on a cell if noteMode is true
    if (this.noteMode) {
      //Find the row of the note value inside the cell
      const n = Math.floor(value/Math.sqrt(this.size))
      //Find the column of the note vallue inside the cell
      const m = value%Math.sqrt(this.size)
      //Check if cell is empty
      if (this.board[x][y] == 0 || this.board[x][y] == null) {
        //Check if the specified note position is zero or null
        if (this.noteBoard[x][y][n][m] == 0 || this.noteBoard[x][y][n][m] == null) {
          //Set note value in the specified position
          this.noteBoard[x][y][n][m] = value + 1
        } else {
          //Remove note value in the specified position
          this.noteBoard[x][y][n][m] = 0
        }
      }
    }
    else {
      //Check if cell value is zero or null
      if (this.preDefined[x][y] == 0 || this.preDefined[x][y] == null) {
        //Set cell value
        this.board[x][y] = value + 1
      }
    //Return back cell position handler to original state[no cell selected state]
    this.setPosition(-1,-1)
    //Call api to update value update on the specified position
    this.makeMove(x, y, value)  
    } 
  }

  //Get selected position
  getPosition() {
    return this.clickedBoxPosition
  }

  //Set position handler with the selected position
  setPosition(row: number, col: number) {
    this.clickedBoxPosition = [row, col]
  }

  //Return back the board to the state where all moves are correct
  undoAll() {
    this.apiService.undoUntilCorrect({session_id: this.session_id}).subscribe({
      next: (res: any) => {
        if (res?.success) this.board = res?.updated_grid
      }
    })
  }

  //Remove the last move only
  undoLast() {
    this.apiService.undoMove({session_id: this.session_id}).subscribe({
      next: (res: any) => {
        if (res?.success) this.board = res?.updated_grid
      }
    })
  }

  //Check if each cell have a value
  isCompeleted():boolean {
    for(let i=0; i<this.size; i++){
      for(let j=0; j<this.size; j++){
        if (this.board[i][j] == 0 || this.board[i][j] == null) return false
      }
    }
    return true
  }

  //Check if the game is compeleted is succefully
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

  //Get specific hint if a cell is selected
  //Get random hint if a cell is not selected
  hint(row: number, col: number) {
    this.apiService.getHint({
      session_id: this.session_id,
      //Check if a cell is selected or not
      selected_cell: row && row > -1 ? {row: row,col: col} : {}
    }).subscribe({
      next: (res: any) => {
        //Assign hint position row
        this.hintRow = res?.hint_row
        //Assign hint position column
        this.hintCol = res?.hint_col
        //Set the board value with hint value
        this.board[this.hintRow][this.hintCol] = res?.hint_value
        //Remove wrong move status which is red color
        this.wrongMoves[this.hintRow][this.hintCol] = false
        setTimeout(() => {
          this.hintRow = -1
          this.hintCol = -1
          //Return back cell position handler to original state[no cell selected state]
          this.setPosition(-1,-1)
        }, 1000)
      }
    })
  }

  //Control action buttons states
  setAction(action: string) {
    this.action = action
    if (action == 'UNDO LAST') {
      this.undoLast()
    }
    if (action == 'UNDO ALL') {
      this.undoAll()
    }
    if (action == 'CHECK') {
      this.filterWrongMoves()
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

  //Update current game time to backend in seconds
  updateTime() {
    const {hours, minutes, seconds} = this.time.get()
    const totalTime = hours*3600 + minutes*60 + seconds
    this.apiService.updateTime({
      board_id: this.boardId,
      time_taken: totalTime
    });
  }

  filterWrongMoves() {
    this.apiService.getIncorrectMoves({
      session_id: this.session_id,
      current_grid_state: this.board
    }).subscribe({
      next: (res: any) => {
        for (let position of Object.keys(res?.wrong_moves)){
          const i = JSON.parse(position)[0]
          const j = JSON.parse(position)[1]
          if (this.board[i][j] && this.board[i][j] > 0) {
            this.wrongMoves[i][j] = true
          }
        }
      }
    })
  }

  //Handle timer state
  handleTime() {
    this.isTimePaused = !this.isTimePaused
    if (this.isTimePaused){
      //Stop timer
      this.time.stop()
    } else {
      //Resume timer
      this.time.resume()
    }
  }

  //Don't display note values initialized with zero
  clearNote(x: number, y: number ) {
    if (this.board[x][y] > 0) {
      return false
    }
    return true
  }
}
