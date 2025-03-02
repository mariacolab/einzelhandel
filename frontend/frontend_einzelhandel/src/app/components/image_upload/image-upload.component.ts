import {Component, EventEmitter, Output} from '@angular/core';
import { CommonModule } from '@angular/common';
import { NgxFileDropEntry, FileSystemFileEntry, FileSystemDirectoryEntry } from 'ngx-file-drop';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { NgxFileDropModule } from 'ngx-file-drop';
import { MatSnackBarModule, MatSnackBar } from '@angular/material/snack-bar';
import { CookieService } from 'ngx-cookie-service';
import {environment} from '../../../environment';

@Component({
  selector: 'app-image-upload',
  standalone: true,
  imports: [CommonModule, NgxFileDropModule, MatSnackBarModule],
  templateUrl: './image-upload.component.html',
  styleUrls: ['./image-upload.component.scss']
})
export class ImageUploadComponent {
  @Output() fileUploaded: EventEmitter<void> = new EventEmitter();
  public file: NgxFileDropEntry[] = [];
  public uploadedFileName: string = "";

  constructor(
    private http: HttpClient,
    private snackBar: MatSnackBar,
    private cookieService: CookieService
  ) {}

  public dropped(event: NgxFileDropEntry[]): void {
    this.file = event;

    for (const droppedFile of event) {
      if (droppedFile.fileEntry.isFile) {
        const fileEntry = droppedFile.fileEntry as FileSystemFileEntry;
        fileEntry.file((file: File) => {
          console.log(droppedFile.relativePath, file);
          this.sendFileToEndpoint(file);
        });
      } else {
        const fileEntry = droppedFile.fileEntry as FileSystemDirectoryEntry;
        console.log(droppedFile.relativePath, fileEntry);
      }
    }
    this.fileUploaded.emit();
  }

  public fileOver(event: Event){
    console.log(event);
  }

  public fileLeave(event: Event){
    console.log(event);
  }

  private sendFileToEndpoint(file: File,) {
    const formData = new FormData();
    formData.append('type', 'ProcessFiles');
    formData.append('filename', file);

    const sessionCookie = this.cookieService.get('session');
    new HttpHeaders({
      'Cookie': `session=${sessionCookie}`
    });
    this.http.post( environment.apiUrls.eventingService.imageUploaded, formData, {
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
    this.fileUploaded.emit();
  }

}
