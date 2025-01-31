import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { LevelComponent } from './level/level.component';
import { BoardComponent } from './board/board.component';
import { CdTimerModule } from 'angular-cd-timer';
import { HttpClientModule } from '@angular/common/http';
import { FormsModule } from '@angular/forms';
import { CongradulationComponent } from './congradulation/congradulation.component';
import { NavbarComponent } from './navbar/navbar.component';
import { FooterComponent } from './footer/footer.component';

@NgModule({
  declarations: [
    AppComponent,
    LevelComponent,
    BoardComponent,
    CongradulationComponent,
    NavbarComponent,
    FooterComponent,
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    CdTimerModule,
    HttpClientModule,
    FormsModule
  ],
  providers: [],
  bootstrap: [AppComponent]
})

export class AppModule { }
