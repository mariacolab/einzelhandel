import { Component, inject } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatToolbarModule } from '@angular/material/toolbar';
import { Router, RouterLink } from '@angular/router';
import { AuthService } from '../auth.service';

@Component({
  selector: 'app-navbar',
  imports: [RouterLink, MatToolbarModule, MatIconModule, MatButtonModule],
  templateUrl: './navbar.component.html',
  styleUrl: './navbar.component.scss'
})
export class NavbarComponent {
  authService = inject(AuthService);
  router = inject(Router);
  public logout() {
    this.authService.logout();
    this.router.navigate(['/login']);
  }
}