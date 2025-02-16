import { Component } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatGridListModule } from '@angular/material/grid-list';
import { MatIconModule } from '@angular/material/icon';
import { MatListModule } from '@angular/material/list';
import { MatSelectModule } from '@angular/material/select';

interface ImageCards {
  avatar: string;
  class: string;
}

@Component({
  selector: 'app-employee',
  imports: [MatListModule, MatIconModule, MatFormFieldModule, MatSelectModule, MatCardModule, MatButtonModule, MatGridListModule],
  templateUrl: './employee.component.html',
  styleUrl: './employee.component.scss'
})
export class EmployeeComponent {
  imageCards: ImageCards[] = [
    { avatar: 'apple', class: 'apple' },
    { avatar: 'banana', class: 'banana' },
    { avatar: 'cucumber', class: 'cucumber' },
    { avatar: 'apple', class: 'apple' },
    { avatar: 'banana', class: 'banana' },
  ];
  objectClasses: string[] = [
    'Apfel', 'Aubergine', 'Avocado', 'Banane', 'Birne', 'Bohnen', 'Cerealien', 'Chips', 'Essig', 'Fisch', 'Gewuerze', 'Granatapfel', 'Honig', 'Kaffee', 'Kaki', 'Karotte', 'Kartoffel', 'Kiwi', 'Knoblauch', 'Kuchen', 'Mais', 'Mandarine', 'Mango', 'Marmelade', 'Mehl', 'Milch', 'Nudeln', 'Nuss', 'Oel', 'Orange', 'Pampelmuse', 'Paprika', 'Pflaume', 'Reis', 'Saft', 'Schokolade', 'Soda', 'Suessigkeit', 'Tee', 'Tomate', 'Tomatensauce', 'Wasser', 'Zitrone', 'Zucchini', 'Zucker', 'Zwiebel'
  ];
  selected = 'option2';
}
