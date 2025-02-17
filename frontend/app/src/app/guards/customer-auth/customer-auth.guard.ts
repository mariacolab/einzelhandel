import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { AuthService } from '../../services/auth/auth.service';

export const customerAuthGuard: CanActivateFn = (route, state) => {
  const authService = inject(AuthService);
  const router = inject(Router);

  if (authService.isLoggedInAsCustomer()) {
    return true;
  } else {
    router.navigate(['/login']);
    // router.createUrlTree(['/login']);
    return false;
  }
};
