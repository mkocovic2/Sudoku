import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { LevelComponent } from './level/level.component';
import { BoardComponent } from './board/board.component';
import { CongradulationComponent } from './congradulation/congradulation.component';

const routes: Routes = [
  {
    path: '',
    component: LevelComponent
  },
  {
    path: 'board',
    component: BoardComponent
  },
  {
    path: 'congradulation',
    component: CongradulationComponent
  }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
