import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { AuthService } from '../../services/auth/auth.service';
import { Router } from '@angular/router';

@Component({
  selector: 'app-dashboard',
  imports: [CommonModule],
  templateUrl: './dashboard.component.html',
  styleUrl: './dashboard.component.scss'
})
export class DashboardComponent implements OnInit {
  userRole: string = '';

  constructor(private authService: AuthService, private router: Router) {}

  ngOnInit(): void {
    this.authService.getUserRole().subscribe(role => {
      this.userRole = role;
      console.log("Benutzerrolle:", role);
      console.log("Rolle", this.userRole);
    });
  }

  openPhotoComponent() {
    this.router.navigate(['/photo']);
  }

  openQrScanner() {
    this.router.navigate(['/qr-code-scanner']);
  }

  openClassification() {
    if (this.userRole === 'Mitarbeiter' || this.userRole === 'Admin') {
      this.router.navigate(['/classification']);
    }
  }

  openTraining() {
    if (this.userRole === 'Admin') {
      this.router.navigate(['/train']);
    }
  }
}
