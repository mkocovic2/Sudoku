import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { LevelComponent } from './level/level.component';
import { NewGameComponent } from './new-game/new-game.component';
import { BoardComponent } from './board/board.component';

const routes: Routes = [
  {
    path: '',
    component: NewGameComponent
  },
  {
    path: 'levels',
    component: LevelComponent
  },
  {
    path: 'new-game',
    component: NewGameComponent
  },
  {
    path: 'board',
    component: BoardComponent
  }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
