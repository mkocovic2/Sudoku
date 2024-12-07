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
  
  startPuzzle(data:any) {
    const path = `${environment.baseUrl}/start_puzzle`;
    return this.http.post(path, data)
  }

  makeMove(data:any) {
    const path = `${environment.baseUrl}/process_move`;
    return this.http.post(path, data)
  }

  checkSolution(data:any) {
    const path = `${environment.baseUrl}/check_solution`;
    return this.http.post(path, data)
  }

  undoMove(data: any) {
    const path = `${environment.baseUrl}/undo_move`;
    return this.http.post(path, data)
  }

  undoUntilCorrect(data: any) {
    const path = `${environment.baseUrl}/undo_until_correct`;
    return this.http.post(path, data)
  }

  getHint(data: any) {
    const path = `${environment.baseUrl}/get_hint`;
    return this.http.post(path, data)
  }

  loadBoard(data: any) {
    const path = `${environment.baseUrl}/load_board`;
    return this.http.post(path, data)
  }

  updateBoard(board: any) {
    this.boardCache.next(board)
  }
}
