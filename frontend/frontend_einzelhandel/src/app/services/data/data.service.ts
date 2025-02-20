import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import { HttpHeaders } from '@angular/common/http';
import { CookieService } from 'ngx-cookie-service';

@Injectable({
  providedIn: 'root'
})
export class DataService {
  // constructor() { }
  // constructor(private http: HttpClient) { }
  constructor(
    private http: HttpClient,
    private cookieService: CookieService
  ) {}

  private token: string = '';
  private baseUrl = 'https://jsonplaceholder.typicode.com'; // Example API URL

  setToken(token: string) {
    this.token = token;
  }

  getToken(): string {
    console.warn(this.token);
    return this.token;
  }

  // Get all posts
  getPosts(): Observable<any> {
    return this.http.get(`${this.baseUrl}/posts`);
  }

  // Get a single post by ID
  getPostById(id: number): Observable<any> {
    return this.http.get(`${this.baseUrl}/posts/${id}`);
    // return await lastValueFrom(this.http.get(`${this.baseUrl}/posts/${id}`));
  }

  postformData(img: File): Observable<any> {
    const url = 'http://localhost/eventing-service/publish/ImageUploaded';
    const formData = new FormData();
    formData.append('type', 'ProcessFiles');
    // formData.append('filename', file, file.name);
    formData.append('filename', img, 'test.jpg');
    formData.append('model', 'small');

    return this.http.post(url, formData, {
      headers: {
        // 'X-Debug-Level': 'verbose',
        'Authorization': 'Bearer ' + JSON.parse(this.token).token
      }
    });
    // .subscribe()
  }

  // From Maria's image-upload-component
  sendFileToEndpoint(file: File,) {
    const formData = new FormData();
    formData.append('type', 'ProcessFiles');
    formData.append('filename', file);
    const sessionCookie = this.cookieService.get('session');
    const headers = new HttpHeaders({
      'Cookie': `session=${sessionCookie}`
    });

    this.http.post('http://localhost:8080/eventing-service/publish/ImageUploaded', formData, {
      withCredentials: true
    }).subscribe(
      response => {
        console.log("Datei an externen Service gesendet:", response);
        // this.snackBar.open('Datei erfolgreich gesendet', 'OK', { duration: 3000 });
      },
      error => {
        console.error("Fehler beim Senden an API:", error);
        // this.snackBar.open('Fehler beim Senden', 'Fehler', { duration: 3000 });
      }
    );
  }
}
