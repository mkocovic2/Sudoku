import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { LevelComponent } from './level/level.component';
import { NewGameComponent } from './new-game/new-game.component';
import { BoardComponent } from './board/board.component';
import { CdTimerModule } from 'angular-cd-timer';

@NgModule({
  declarations: [
    AppComponent,
    LevelComponent,
    NewGameComponent,
    BoardComponent,
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    CdTimerModule
  ],
  providers: [],
  bootstrap: [AppComponent]
})

export class AppModule { }
