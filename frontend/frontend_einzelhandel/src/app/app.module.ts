import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { HttpClientModule } from '@angular/common/http';
import { CommonModule } from '@angular/common';

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

// Komponenten
import { AppComponent } from './app.component';
import { PhotoComponent } from './components/photo/photo.component';
import { PhotoEmpComponent } from './components/photo_emp/photo_emp.component';

@NgModule({
  declarations: [
    AppComponent,
    PhotoComponent,
    PhotoEmpComponent
  ],
  imports: [
    BrowserModule,
    FormsModule,
    HttpClientModule,
    CommonModule,
    MatIconModule,
    MatButtonModule,
    MatCardModule,
    MatGridListModule,
    MatFormFieldModule,
    MatSelectModule,
    MatInputModule,
    WebcamModule,
    NgxFileDropModule,
    NgIf
  ],
  exports: [EmployeeComponent],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule {}
