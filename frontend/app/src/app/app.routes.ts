import { Routes } from '@angular/router';
import { CustomerComponent } from './components/customer/customer.component';
import { EmployeeComponent } from './components/employee/employee.component';
import { LoginComponent } from './components/login/login.component';
import { PhotoComponent } from './components/photo/photo.component';
import { ProductDetailsComponent } from './components/product-details/product-details.component';
import { QrcodeComponent } from './components/qrcode/qrcode.component';
import { SignUpComponent } from './components/sign-up/sign-up.component';
import { authGuard } from './guards/auth/auth.guard';
import { notLoggedInAuthGuard } from './guards/not-logged-in-auth/not-logged-in-auth.guard';

export const routes: Routes = [
  { path: '', redirectTo: '/login', pathMatch: 'full' },
  { path: 'signup', component: SignUpComponent },
  // { path: 'login', component: LoginComponent },
  { path: 'login', component: LoginComponent, canActivate: [notLoggedInAuthGuard] },
  // { path: 'admin', component: AdminComponent, canActivate: [authGuard] },
  // { path: 'customer', component: CustomerComponent },
  { path: 'customer', component: CustomerComponent, canActivate: [authGuard] },
  { path: 'employee', component: EmployeeComponent, canActivate: [authGuard] },
  // { path: 'photo', component: PhotoComponent },
  { path: 'photo', component: PhotoComponent, canActivate: [authGuard] },
  // { path: 'qrcode', component: QrcodeComponent }
  { path: 'qrcode', component: QrcodeComponent, canActivate: [authGuard] },
  { path: 'product-details', component: ProductDetailsComponent, canActivate: [authGuard] }
];