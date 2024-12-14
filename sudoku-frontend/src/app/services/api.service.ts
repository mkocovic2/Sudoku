import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';
import { environment } from 'src/environments/environment';

@Injectable({
  providedIn: 'root'
})
export class ApiService {

  constructor(private http: HttpClient) { }

  boardCache = new BehaviorSubject<any>({})
  boardObs = this.boardCache.asObservable()
  
  //API service to start a puzzle
  startPuzzle(data:any) {
    const path = `${environment.baseUrl}/start_puzzle`;
    return this.http.post(path, data)
  }

  //API service to update each cell move
  makeMove(data:any) {
    const path = `${environment.baseUrl}/process_move`;
    return this.http.post(path, data)
  }

  //API service to check if game is compeleted successfully
  checkSolution(data:any) {
    const path = `${environment.baseUrl}/check_solution`;
    return this.http.post(path, data)
  }

  //API service to get incorrect moves
  getIncorrectMoves(data: any) {
    const path = `${environment.baseUrl}/store_incorrect_moves`;
    return this.http.post(path, data)
  }
  
  //API service to undo last move only
  undoMove(data: any) {
    const path = `${environment.baseUrl}/undo_move`;
    return this.http.post(path, data)
  }

  //API service to return back the puzzle to the state where all moves are correct
  undoUntilCorrect(data: any) {
    const path = `${environment.baseUrl}/undo_until_correct`;
    return this.http.post(path, data)
  }

  //API service to update the time the user stopped playing
  updateTime(data: any) {
    const endpoint = `${environment.baseUrl}/save_time`;
  
    fetch(endpoint, {
      method: 'POST',
      body: JSON.stringify(data),
      headers: { 'Content-Type': 'application/json' },
      keepalive: true,
    });
  }

  //API service to get both random and specific hint
  getHint(data: any) {
    const path = `${environment.baseUrl}/get_hint`;
    return this.http.post(path, data)
  }

  //API service to load a specific board with boardId given
  loadBoard(data: any) {
    const path = `${environment.baseUrl}/load_board`;
    return this.http.post(path, data)
  }

  //Observer initialized to pass the board value from one route to another route
  updateBoard(board: any) {
    this.boardCache.next(board)
  }
}
