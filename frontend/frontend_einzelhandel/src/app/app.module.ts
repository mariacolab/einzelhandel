import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { HttpClientModule } from '@angular/common/http';
import {CommonModule, NgIf} from '@angular/common';

// Angular Material Module
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatGridListModule } from '@angular/material/grid-list';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { WebcamModule } from 'ngx-webcam';
import { NgxFileDropModule } from 'ngx-file-drop';
import { ZXingScannerModule } from '@zxing/ngx-scanner';

// Komponenten
import { AppComponent } from './app.component';
import { PhotoComponent } from './components/photo/photo.component';
import { QrcodeComponent } from './components/qrcode/qrcode.component';
import {WebsocketService} from './services/websocket/websocket.service';
import {LoginComponent} from './components/login/login.component';
import {UnauthorizedComponent} from './components/unauthorized/unauthorized.component';
import {DashboardComponent} from './components/dashboard/dashboard.component';
import {TrainComponent} from './components/train/train.component';
import {MatListModule} from '@angular/material/list';
import {MatOptionModule} from '@angular/material/core';

@NgModule({
  declarations: [
    AppComponent,
    DashboardComponent,
    TrainComponent,
    PhotoComponent,
    LoginComponent,
    QrcodeComponent,
    UnauthorizedComponent
  ],
  imports: [
    BrowserModule,
    FormsModule,
    HttpClientModule,
    CommonModule,
    FormsModule,
    MatIconModule,
    MatButtonModule,
    MatCardModule,
    MatGridListModule,
    MatListModule,
    MatOptionModule,
    MatFormFieldModule,
    MatSelectModule,
    MatInputModule,
    WebcamModule,
    NgxFileDropModule,
    NgIf,
    ZXingScannerModule
  ],
  exports: [WebsocketService, MatIconModule],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule {}
