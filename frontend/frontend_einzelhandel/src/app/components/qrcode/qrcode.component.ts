import { Component, inject } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatSnackBar } from '@angular/material/snack-bar';
import { ZXingScannerModule } from '@zxing/ngx-scanner';

import { Router, RouterModule } from '@angular/router';
import { NgIf } from '@angular/common';


@Component({
  selector: 'app-qrcode',
  imports: [ZXingScannerModule, MatIconModule, MatButtonModule, RouterModule, NgIf],
  templateUrl: './qrcode.component.html',
  styleUrl: './qrcode.component.scss'
})
export class QrcodeComponent {
  scannerEnabled = true;
  private scannedString: string = '';
  private _snackBar = inject(MatSnackBar);
  scanSuccess = false;

  // scanSuccessHandler(event: string) {
  // }

  // scanErrorHandler(event: EventEmitter<any>) {
  // }
  
  // scanFailureHandler(event: EventEmitter<void>) {
  // }

  // scanCompleteHandler(event: EventEmitter<any>) {
  // }

  scanSuccessHandler(event: string) {
    this.scannedString = event;
    // this.scannerEnabled = false;
    // console.log(this.scannedString)
    // this._snackBar.open(this.scannedString);
    // this.snackBar.open('Scan successfull!', '', {duration: 1000});
    // this.scanSuccess = true;
    // this.fakeIt();
  }

  scanErrorHandler(event: any) {
  }

  scanFailureHandler(event: any) {
  }

  scanCompleteHandler(event: any) {
    // console.log('scanCompleteHandler()');
    // this._snackBar.open(this.scannedString);
    this.snackBar.open('Scan successfull!', '', {duration: 1000});
    this.scanSuccess = true;
    // this.fakeIt();
    // console.log(this.scanSuccess);
  }

  toggleScanner() {
    this.scannerEnabled = !this.scannerEnabled;
    this.scanSuccess = false;
  }

  snackBar = inject(MatSnackBar);
  router = inject(Router);
  fakeIt() {
    this.snackBar.open('Analysing. Please wait...', '', {duration: 500});
    // this.router.navigate(['/product-details']);
    setTimeout(() => {this.router.navigate(['product-details'])}, 500);
  }
}
