import { Component, inject } from '@angular/core';
import { FormControl, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatInputModule } from '@angular/material/input';
import { MatSnackBar } from '@angular/material/snack-bar';
import { Router, RouterModule } from '@angular/router';
import { AuthService } from '../auth.service';

@Component({
  selector: 'app-sign-up',
  imports: [RouterModule, ReactiveFormsModule, MatInputModule, MatButtonModule],
  templateUrl: './sign-up.component.html',
  styleUrl: './sign-up.component.scss'
})
export class SignUpComponent {
  authService = inject(AuthService);
  router = inject(Router);
  constructor(public snackBar: MatSnackBar) { }

  protected loginForm = new FormGroup({
    // email: new FormControl('', [Validators.required, Validators.email]),
    username: new FormControl('', [Validators.required]),
    password: new FormControl('', [Validators.required])
  })

  signUp() {
    if (this.loginForm.valid) {
      console.log(this.loginForm.value);
      this.authService.signUp(this.loginForm.value)
        .subscribe({
          next: (data: any) => {
            // if(this.authService.isLoggedIn()){
            //   // this.router.navigate(['/admin']);
            //   this.router.navigate(['/login']);
            // }
            console.log('signed up!');
            this.snackBar.open('Sign up succeeded', 'Dismiss', {
              duration: 3000
            });
            this.router.navigate(['/login']);
          },
          error: (err: any) => {
            console.log(err)
            this.snackBar.open('Sign up failed', 'Dismiss', {
              duration: 3000
            });
          }
        });
    }
  }
}
