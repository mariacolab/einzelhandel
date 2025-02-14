import { Routes } from '@angular/router';
import { authGuard } from './auth.guard';
import { EmployeeComponent } from './employee/employee.component';
import { LoginComponent } from './login/login.component';
import { notLoggedInAuthGuard } from './not-logged-in-auth.guard';
import { PhotoComponent } from './photo/photo.component';
import { QrcodeComponent } from './qrcode/qrcode.component';
import { SignUpComponent } from './sign-up/sign-up.component';
import { ProductDetailsComponent } from './product-details/product-details.component';

export const routes: Routes = [
    { path: '', redirectTo: '/login', pathMatch: 'full' },
    { path: 'signup', component: SignUpComponent },
    // { path: 'login', component: LoginComponent },
    { path: 'login', component: LoginComponent, canActivate: [notLoggedInAuthGuard] },
    // { path: 'admin', component: AdminComponent, canActivate: [authGuard] },
    // { path: 'employee', component: EmployeeComponent, canActivate: [authGuard] },
    { path: 'employee', component: EmployeeComponent },
    { path: 'employee', component: EmployeeComponent, canActivate: [authGuard] },
    // { path: 'customer', component: CustomerComponent, canActivate: [authGuard] },
    // { path: 'photo', component: PhotoComponent },
    { path: 'photo', component: PhotoComponent, canActivate: [authGuard] },
    // { path: 'qrcode', component: QrcodeComponent }
    { path: 'qrcode', component: QrcodeComponent, canActivate: [authGuard] },
    { path: 'product-details', component: ProductDetailsComponent, canActivate: [authGuard] }
];
