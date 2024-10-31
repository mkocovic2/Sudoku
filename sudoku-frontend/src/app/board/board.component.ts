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

  clickCell = (i:number, j:number) => {
    this.clickedBoxPosition = [i, j]
  }
}
