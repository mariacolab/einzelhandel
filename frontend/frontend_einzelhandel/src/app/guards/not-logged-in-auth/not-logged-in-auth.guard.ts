import { inject } from '@angular/core';
import {CanActivateFn, Router} from '@angular/router';
import { AuthService } from '../../services/auth/auth.service';
import {map} from 'rxjs';

export const notLoggedInAuthGuard: CanActivateFn = (route, state) => {
  const authService = inject(AuthService);
  const router = inject(Router);

  return authService.isLoggedIn().pipe(
    map(isLoggedIn => {
      if (!isLoggedIn) {
        return true; // Benutzer ist nicht eingeloggt → Zugriff erlauben
      } else {
        router.navigate(['/dashboard']); // Benutzer ist eingeloggt
        return false;
      }
    })
  );
};
