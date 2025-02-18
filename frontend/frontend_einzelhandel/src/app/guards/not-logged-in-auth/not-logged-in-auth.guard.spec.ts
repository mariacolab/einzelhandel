import { TestBed } from '@angular/core/testing';
import { CanActivateFn } from '@angular/router';

import { notLoggedInAuthGuard } from './not-logged-in-auth.guard';

describe('notLoggedInAuthGuard', () => {
  const executeGuard: CanActivateFn = (...guardParameters) => 
      TestBed.runInInjectionContext(() => notLoggedInAuthGuard(...guardParameters));

  beforeEach(() => {
    TestBed.configureTestingModule({});
  });

  it('should be created', () => {
    expect(executeGuard).toBeTruthy();
  });
});
