import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import {environment} from '../../../environment';

@Injectable({
  providedIn: 'root'
})
export class DataService {
  // constructor() { }
  constructor(private http: HttpClient) { }

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
    const url = environment.apiUrls.eventingService.imageUploaded;
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
}
