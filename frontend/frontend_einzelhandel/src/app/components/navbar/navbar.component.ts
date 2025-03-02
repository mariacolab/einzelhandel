import { Component, inject } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatToolbarModule } from '@angular/material/toolbar';
import {NavigationEnd, Router, RouterLink} from '@angular/router';
import { AuthService } from '../../services/auth/auth.service';
import {CommonModule} from '@angular/common';

@Component({
  selector: 'app-navbar',
  imports: [MatToolbarModule, MatButtonModule, CommonModule, MatIconModule],
  templateUrl: './navbar.component.html',
  styleUrl: './navbar.component.scss'
})
export class NavbarComponent {
  authService = inject(AuthService);
  router = inject(Router);
  showNavbar = true;

  constructor() {
    this.router.events.subscribe(event => {
      if (event instanceof NavigationEnd) {
        // Navbar nur anzeigen, wenn NICHT auf Login oder Signup Seite
        this.showNavbar = !['/login', '/signup'].includes(event.url);
      }
    });
  }

  public logout() {
    this.authService.logout();
    this.router.navigate(['/login']);
  }

  public navigateToDashboard() {
    this.router.navigate(['/dashboard']);
  }

  public navigateToCustomer() {
    this.router.navigate(['/customer']);
  }

  public navigateToEmployee() {
    this.router.navigate(['/employee']);
  }
}
