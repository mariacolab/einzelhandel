import { Component, inject } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatSnackBar } from '@angular/material/snack-bar';
import { ZXingScannerModule } from '@zxing/ngx-scanner';

@Component({
  selector: 'app-qrcode',
  imports: [ZXingScannerModule, MatIconModule, MatButtonModule],
  templateUrl: './qrcode.component.html',
  styleUrl: './qrcode.component.scss'
})
export class QrcodeComponent {
  scannerEnabled = true;
  private scannedString: string = '';
  private _snackBar = inject(MatSnackBar);
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
  }
  scanErrorHandler(event: any) {

  }
  scanFailureHandler(event: any) {

  }
  scanCompleteHandler(event: any) {
    // console.log('scanCompleteHandler()');
    // this._snackBar.open(this.scannedString);
  }
}
