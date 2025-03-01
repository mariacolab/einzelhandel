import {Component, OnInit, OnDestroy, Injectable, ChangeDetectorRef} from '@angular/core';
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
import {HttpClient, HttpHeaders} from '@angular/common/http';
import { FormsModule } from '@angular/forms';
import {MatSnackBar} from '@angular/material/snack-bar';
import {environment} from '../../../environment';

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
   selectedOptions: { [key: number]: string } = {};
  training: any = null;

      constructor(private snackBar: MatSnackBar,
                  private websocketService: WebsocketService,
                  private http: HttpClient,
                  private cdRef: ChangeDetectorRef) {}

      ngOnInit() {
        this.websocketService.ngOnInit();

        this.subscriptions.push(
          this.websocketService.getTrainingDataTF().subscribe(data => {
            if (data && data.files) {
              console.log("Empfangene Trainingsdaten (TF):", data);
              this.training = data;
              this.cdRef.detectChanges();
              this.selectedOptions = new Array(data.files.length).fill('Unclassified');
            }
          })
        );

        this.websocketService.getLabeledTrainingAck().subscribe(msg => {
          console.log("Labeling abgeschlossen:", msg);
          // Hier könntest du z. B. eine Benachrichtigung anzeigen
        });

        console.log('Training Data:', this.training);
        console.log('Object Classes:', this.objectClasses);
        console.log('Selected Options:', this.selectedOptions);
      }

      isValidBase64Image(base64String: unknown): boolean {
        if (typeof base64String !== "string") {
          return false;
        }
        return base64String.startsWith("/9j/") || base64String.startsWith("iVBOR");
      }

      submitLabels() {
        this.websocketService.socket.on('connect', () => {
          console.log('WebSocket connected');
        });

        const payload = {
          ki: this.training.ki,
          fileNames: this.training.files,
          labels: this.selectedOptions
        };
        console.log("Label payload erhalten: ", payload)
          this.websocketService.sendLabeledTrainingDataTf(payload);
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
    const formData = new FormData();
    formData.append('type', 'LabeledTrainingdata');
    formData.append('files', this.training.files);
    formData.append('labels', JSON.stringify(this.selectedOptions));
    formData.append('ki', this.training.ki);
    console.log("Selected Labels:", formData);
    this.http.post(environment.apiUrls.eventingService.labeledTrainingData, formData, {
      withCredentials: true
    }).subscribe(
      response => {
        console.log("Datei an externen Service gesendet:", response);
        this.snackBar.open('Datei erfolgreich gesendet', 'OK', { duration: 3000 });
      },
      error => {
        console.error("Fehler beim Senden an API:", error);
        this.snackBar.open('Fehler beim Senden', 'Fehler', { duration: 3000 });
      }
    );
  }
  ngOnDestroy() {
    this.subscriptions.forEach(sub => sub.unsubscribe());
    console.log('Klassifikation wird verlassen. WebSockets schließen.');
    this.websocketService.ngOnDestroy();
  }

  imageCards: ImageCards[] = [
    { avatar: 'apple', class: 'apple' },
    { avatar: 'banana', class: 'banana' },
    { avatar: 'cucumber', class: 'cucumber' },
    { avatar: 'apple', class: 'apple' },
    { avatar: 'banana', class: 'banana' },
  ];
  objectClasses: string[] = [
    'Apfel', 'Aubergine', 'Avocado', 'Birne',
    'Granatapfel', 'Kaki', 'Kartoffel', 'Kiwi',
    'Mandarine', 'Orange', 'Pampelmuse', 'Paprika',
    'Tomate', 'Zitrone', 'Zucchini', 'Zwiebel'
  ];
  selected = 'option2';
}
