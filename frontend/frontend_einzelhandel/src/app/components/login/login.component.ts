import { Component, inject, signal } from '@angular/core';
import { FormControl, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatGridListModule } from '@angular/material/grid-list';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatRadioModule } from '@angular/material/radio';
import { MatSelectModule } from '@angular/material/select';
import { MatSnackBar } from '@angular/material/snack-bar';
import { Router, RouterModule } from '@angular/router';
import { AuthService } from '../../services/auth/auth.service';

@Component({
  selector: 'app-login',
  imports: [
    ReactiveFormsModule,
    RouterModule,
    MatInputModule,
    MatButtonModule,
    MatSelectModule,
    MatRadioModule,
    MatCardModule,
    MatGridListModule,
    MatIconModule
  ],
  templateUrl: './login.component.html',
  styleUrl: './login.component.scss',
})
export class LoginComponent {
  //authService = inject(AuthService);
  //router = inject(Router);
  // snackBar = inject(MatSnackBar);
  // snackBar = inject(MatSnackBarModule);
  constructor(public snackBar: MatSnackBar, private authService: AuthService, private router: Router) {}


  protected loginForm = new FormGroup({
    // email: new FormControl('', [Validators.required, Validators.email]),
    username: new FormControl('', [Validators.required]),
    password: new FormControl('', [Validators.required])
  })

  hide = signal(true);
  clickEvent(event: MouseEvent) {
    this.hide.set(!this.hide());
    event.stopPropagation();
  }

  login() {
    if (this.loginForm.valid) {
      console.log("Login-Daten:", this.loginForm.value); // Debugging
      this.authService.login({
        username: this.loginForm.value.username,
        password: this.loginForm.value.password
      }).subscribe({
        next: (data: any) => {
          console.log("Login erfolgreich!", data);
          this.router.navigate(['/dashboard']);
        },
        error: (err: any) => {
          console.error("Fehler beim Login:", err);
          this.snackBar.open('Login fehlgeschlagen', 'Dismiss', { duration: 3000 });
        }
      });
    }
  }

}
