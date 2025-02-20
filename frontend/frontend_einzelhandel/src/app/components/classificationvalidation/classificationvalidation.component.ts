import { Component, OnInit, OnDestroy, Injectable  } from '@angular/core';
import { CommonModule } from '@angular/common';
import { WebsocketService } from '../../services/websocket/websocket.service';
import { Subscription } from 'rxjs';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatGridListModule } from '@angular/material/grid-list';
import { MatIconModule } from '@angular/material/icon';
import { MatListModule } from '@angular/material/list';
import { MatSelectModule } from '@angular/material/select';
import { HttpClient } from '@angular/common/http';
import { FormsModule } from '@angular/forms';

interface ImageCards {
  avatar: string;
  class: string;
}
@Injectable({
  providedIn: 'root'
})

@Component({
  selector: 'app-classificationvalidation',
  imports: [FormsModule, CommonModule, MatListModule, MatIconModule, MatFormFieldModule, MatSelectModule, MatCardModule, MatButtonModule, MatGridListModule],
  templateUrl: './classificationvalidation.component.html',
  styleUrl: './classificationvalidation.component.scss'
})
export class ClassificationValidationComponent implements OnInit, OnDestroy {

   private subscriptions: Subscription[] = [];
   selectedOptions: string[] = [];
      training: any = null;

      constructor(private websocketService: WebsocketService, private http: HttpClient) {}

      ngOnInit() {
        this.subscriptions.push(
          this.websocketService.getTraining().subscribe(data => {
            console.log("Empfangene Trainingsdaten:", data);  // Debugging

            if (data && data.files) {
              this.training = data;
              this.selectedOptions = new Array(data.files.length).fill('Unclassified'); // Standardwert setzen
            }
          }) // <--- Stelle sicher, dass hier KEIN unnötiges `,` oder fehlendes `;` ist
        );

        this.websocketService.startWatchdog();
      }

      isValidBase64Image(base64String: string): boolean {
          return base64String.startsWith("/9j/") || base64String.startsWith("iVBOR");
        }

        getMimeType(base64String: string): string {
          if (base64String.startsWith("/9j/")) {
            console.log("Trainingdata erhalten:", "image/jpeg");
            return "image/jpg";
          } else if (base64String.startsWith("iVBOR")) {
            console.log("Trainingdata erhalten:", "image/png");
            return "image/png";
          }
          return "image/jpg";
        }

  sendData() {
    const requestData = this.training.files.map((file: string, index: number) => ({
      image: file,
      classification: this.selectedOptions[index] || 'Unclassified'
    }));

    this.http.post<any>('https://example.com/api/save-data', requestData).subscribe((response: any) => {
      console.log('Daten erfolgreich gesendet:', response);
    }, error => {
      console.error('Fehler beim Senden der Daten:', error);
    });
  }

      ngOnDestroy() {
        this.websocketService.stopWatchdog();
        this.subscriptions.forEach(sub => sub.unsubscribe());
      }
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
