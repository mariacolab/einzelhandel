import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { tap } from 'rxjs/operators';
import { DataService } from '../data/data.service';
import {Router} from '@angular/router';
import {map, Observable, pipe} from 'rxjs';
import {environment} from '../../../environment';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  constructor(private http: HttpClient, private router: Router) {}

  baseUrl = environment.apiUrls.userManagement;

  signUp(data: any) {
    return this.http.post(`${this.baseUrl}/register`, data)
      .pipe(tap((response ) => {
        console.log(response );
      }));
  }

  login(data: any): Observable<any> {
    return this.http.post<{ role: string}>(`${this.baseUrl}/login`, data, {
      withCredentials: true,
      observe: 'response'
    }).pipe(
        tap((response: any) => {
          console.log("Login Response:", response);
          if (response && response.status === 200) {
            this.router.navigate(['/dashboard']);
          } else {
            console.error("Login fehlgeschlagen, falsche Credentials!");
          }
        })
      );
  }

  isLoggedIn(): Observable<boolean> {
    return this.http.get<{ loggedIn: boolean }>(`${this.baseUrl}/session`, { withCredentials: true })
      .pipe(map(response => response.loggedIn));
  }

  getUserRole(): Observable<string> {
    return this.http.get<{ role: string }>(`${this.baseUrl}/role`, { withCredentials: true })
      .pipe(map(response => response.role));
  }

  isLoggedInAsCustomer(): Observable<boolean> {
    return this.getUserRole().pipe(map(role => role === 'Kunde'));
  }

  isLoggedInAsEmployee(): Observable<boolean> {
    return this.getUserRole().pipe(map(role => role === 'Mitarbeiter'));
  }

  isLoggedInAsAdmin(): Observable<boolean> {
    return this.getUserRole().pipe(map(role => role === 'Admin'));
  }

  logout(): void {
    this.http.post(`${this.baseUrl}/logout`, {}, { withCredentials: true }).subscribe(() => {
      this.router.navigate(['/login']);
    });
  }
}
