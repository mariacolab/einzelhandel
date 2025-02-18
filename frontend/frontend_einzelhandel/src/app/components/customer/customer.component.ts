import { Component, inject } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { Router, RouterLink } from '@angular/router';
import { AuthService } from '../../services/auth/auth.service';

@Component({
  selector: 'app-customer',
  imports: [RouterLink, MatIconModule, MatButtonModule],
  templateUrl: './customer.component.html',
  styleUrl: './customer.component.scss'
})
export class CustomerComponent {
  authService = inject(AuthService);
  router = inject(Router);

  public logout() {
    this.authService.logout();
    this.router.navigate(['/login']);
  }
}
