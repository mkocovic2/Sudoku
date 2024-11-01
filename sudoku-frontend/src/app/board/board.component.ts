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

  selectCell(i:number, j:number) {
    this.clickedBoxPosition = [i, j]
  }

  setCell(value: number) {
    const [x, y] = this.getPosition()
    if (x > -1 && this.board[x][y] == 0) {
      this.board[x][y] = value
    }
  }

  getPosition() {
    return this.clickedBoxPosition
  }
}
