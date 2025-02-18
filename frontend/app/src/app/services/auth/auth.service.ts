import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { tap } from 'rxjs/operators';
import { DataService } from '../data/data.service';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  // constructor() { }
  dataService = inject(DataService);
  httpClient = inject(HttpClient);

  // baseUrl = 'http://localhost:3000/api';
  baseUrl = 'http://localhost:8080/user-management/auth';

  signUp(data: any) {
    return this.httpClient.post(`${this.baseUrl}/register`, data)
      .pipe(tap((result) => {
        console.log(result);
      }));
  }

  login(data: any) {
    return this.httpClient.post(`${this.baseUrl}/login`, data)
      .pipe(tap((result) => {
        localStorage.setItem('authUser', JSON.stringify(result));
        // console.log(result);
        // console.log(JSON.stringify(result));
        this.dataService.setToken(JSON.stringify(result));
      }));
  }

  logout() {
    localStorage.removeItem('authUser');
  }

  isLoggedIn() {
    return localStorage.getItem('authUser') !== null;
  }

  isLoggedInAsCustomer() {
    return ((localStorage.getItem('authUser') !== null) && (JSON.parse(localStorage.getItem('authUser')!).role_name == 'Kunde'));  // FIXME avoid non-null assertion operator?
  }

  isLoggedInAsEmployee() {
    return ((localStorage.getItem('authUser') !== null) && (JSON.parse(localStorage.getItem('authUser')!).role_name == 'Mitarbeiter')); // FIXME non-null assertion operator?
  }
}
