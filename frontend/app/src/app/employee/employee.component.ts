import { Component, inject } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { Router, RouterLink } from '@angular/router';
import { AuthService } from '../auth.service';

@Component({
  selector: 'app-employee',
  imports: [RouterLink, MatIconModule, MatButtonModule],
  templateUrl: './employee.component.html',
  styleUrl: './employee.component.scss'
})
export class EmployeeComponent {
  authService = inject(AuthService);
  router = inject(Router);

  public logout() {
    this.authService.logout();
    this.router.navigate(['/login']);
  }
}
