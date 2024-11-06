import { Component } from '@angular/core';

@Component({
  selector: 'app-board',
  templateUrl: './board.component.html',
  styleUrls: ['./board.component.scss']
})
export class BoardComponent {

  boxes = Array(9)
  board: number[][] = Array.from({ length: 9 }, () => Array(9).fill(0));
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

  selectCell(i:number, j:number) {
    this.clickedBoxPosition = [i, j]
  }

  setCell(value: number) {
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
    } 
  }

  getPosition() {
    return this.clickedBoxPosition
  }

  setAction(action: string) {
    if (action == 'NOTE') {
      this.noteMode = !this.noteMode
      console.log(this.noteBoard)
    }
  }
}
