import { Component, OnInit } from '@angular/core';
import { animation } from '../../assets/js/animation.js'

@Component({
  selector: 'app-congradulation',
  templateUrl: './congradulation.component.html',
  styleUrls: ['./congradulation.component.scss']
})
export class CongradulationComponent implements OnInit {

  ngOnInit(): void {
    animation()
  }

}
