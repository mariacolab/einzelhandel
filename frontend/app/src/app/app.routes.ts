import { Routes } from '@angular/router';
import { CustomerComponent } from './components/customer/customer.component';
import { EmployeeComponent } from './components/employee/employee.component';
import { LoginComponent } from './components/login/login.component';
import { PhotoComponent } from './components/photo/photo.component';
import { ProductDetailsComponent } from './components/product-details/product-details.component';
import { QrcodeComponent } from './components/qrcode/qrcode.component';
import { SignUpComponent } from './components/sign-up/sign-up.component';
// import { authGuard } from './guards/auth/auth.guard';
import { customerAuthGuard } from './guards/customer-auth/customer-auth.guard';
import { employeeAuthGuard } from './guards/employee-auth/employee-auth.guard';
import { notLoggedInAuthGuard } from './guards/not-logged-in-auth/not-logged-in-auth.guard';

export const routes: Routes = [
  { path: '', redirectTo: '/login', pathMatch: 'full' },
  { path: 'signup', component: SignUpComponent },
  // { path: 'login', component: LoginComponent },
  { path: 'login', component: LoginComponent, canActivate: [notLoggedInAuthGuard] },
  { path: 'customer', component: CustomerComponent, canActivate: [customerAuthGuard] },
  { path: 'photo', component: PhotoComponent, canActivate: [customerAuthGuard] },
  { path: 'qrcode', component: QrcodeComponent, canActivate: [customerAuthGuard] },
  { path: 'product-details', component: ProductDetailsComponent, canActivate: [customerAuthGuard] },
  { path: 'employee', component: EmployeeComponent, canActivate: [employeeAuthGuard] },
  { path: '**', redirectTo: '/login'}
];