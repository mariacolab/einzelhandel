import {Component} from '@angular/core';
import {HttpClient} from '@angular/common/http';
import {transition} from '@angular/animations';
import {CommonModule} from '@angular/common';
import {environment} from '../../../environment';

@Component({
  selector: 'app-train',
  templateUrl: './train.component.html' ,
  styleUrl:'./train.component.scss' ,
  imports: [CommonModule],
})
export class TrainComponent {
  message: string = '';
  baseUrl: string = '';

  constructor(private http: HttpClient) {
  }

  startTraining(model: string) {
    const formData = new FormData();

    if(model == 'yolo'){
      this.baseUrl = environment.apiUrls.eventingService.yolo;
      formData.append('type', 'TrainYOLO');
    } else {
      this.baseUrl = environment.apiUrls.eventingService.tensorflow;
      formData.append('type', 'TrainTF');
    }

    this.http.post(this.baseUrl, formData, {headers: {
        'Accept': 'application/json'
      },
      withCredentials: true
    }).subscribe(
      response => this.message = `${model} Training gestartet!`,
      error => this.message = `Fehler beim Starten des Trainings: ${error.message}`
    );
  }
}
