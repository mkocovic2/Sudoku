import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CongradulationComponent } from './congradulation.component';

describe('CongradulationComponent', () => {
  let component: CongradulationComponent;
  let fixture: ComponentFixture<CongradulationComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [CongradulationComponent]
    });
    fixture = TestBed.createComponent(CongradulationComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
