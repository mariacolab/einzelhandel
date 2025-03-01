import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { LoginComponent } from './components/login/login.component';
import { PhotoComponent } from './components/photo/photo.component';
import { QrcodeComponent } from './components/qrcode/qrcode.component';
import {UnauthorizedComponent} from './components/unauthorized/unauthorized.component';
import {DashboardComponent} from './components/dashboard/dashboard.component';
import {authGuard} from './guards/auth/auth.guard';
import {
  ClassificationValidationComponent
} from './components/classificationvalidation/classificationvalidation.component';
import {TrainComponent} from './components/train/train.component';
import {SignUpComponent} from './components/sign-up/sign-up.component';


export const routes: Routes = [
  { path: '', redirectTo: '/login', pathMatch: 'full' },
  { path: 'dashboard', component: DashboardComponent, canActivate: [authGuard] },
  { path: 'login', component: LoginComponent },
  { path: 'signup', component: SignUpComponent },
  { path: 'unauthorized', component: UnauthorizedComponent },
  { path: 'photo', component: PhotoComponent, canActivate: [authGuard]},
  { path: 'qr-code-scanner', component: QrcodeComponent, canActivate: [authGuard]},
  { path: 'classification', component: ClassificationValidationComponent, canActivate: [authGuard]},
  { path: 'train', component: TrainComponent, canActivate: [authGuard]},
  { path: '**', redirectTo: '/login'}
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
