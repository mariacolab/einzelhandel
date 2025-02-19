import { Routes } from '@angular/router';
import { CustomerComponent } from './components/customer/customer.component';
import { EmployeeComponent } from './components/employee/employee.component';
import { PhotoEmpComponent } from './components/photo_emp/photo_emp.component';
import { LoginComponent } from './components/login/login.component';
import { PhotoComponent } from './components/photo/photo.component';
import { ImageUploadComponent } from './components/image_upload/image-upload.component';
import { ProductDetailsComponent } from './components/product-details/product-details.component';
import { QrcodeComponent } from './components/qrcode/qrcode.component';
import { QrcodeempComponent } from './components/qrcodeemp/qrcodeemp.component';
import { SignUpComponent } from './components/sign-up/sign-up.component';
import { customerAuthGuard } from './guards/customer-auth/customer-auth.guard';
import { employeeAuthGuard } from './guards/employee-auth/employee-auth.guard';
import { MessagesComponent } from './components/messages/messages.component';
import { notLoggedInAuthGuard } from './guards/not-logged-in-auth/not-logged-in-auth.guard';

export const routes: Routes = [
  { path: '', redirectTo: '/login', pathMatch: 'full' },
  { path: 'signup', component: SignUpComponent },
  { path: 'login', component: LoginComponent, canActivate: [notLoggedInAuthGuard] },
  { path: 'customer', component: CustomerComponent, canActivate: [customerAuthGuard] },
  { path: 'photo', component: PhotoComponent, canActivate: [customerAuthGuard] },
  { path: 'qrcode', component: QrcodeComponent, canActivate: [customerAuthGuard] },
  { path: 'product-details', component: ProductDetailsComponent, canActivate: [customerAuthGuard] },
  { path: 'image_upload', component: ImageUploadComponent, canActivate: [customerAuthGuard] },
  { path: 'employee', component: EmployeeComponent, canActivate: [employeeAuthGuard] },
  { path: 'messages', component: MessagesComponent, canActivate: [employeeAuthGuard] },
  { path: 'photo_emp', component: PhotoEmpComponent, canActivate: [employeeAuthGuard] },
  { path: 'qrcodeemp', component: QrcodeempComponent, canActivate: [employeeAuthGuard] },
  { path: '**', redirectTo: '/login'}
];
