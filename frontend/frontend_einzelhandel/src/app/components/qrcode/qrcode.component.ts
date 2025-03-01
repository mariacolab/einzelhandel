import {Component, ElementRef, inject, OnDestroy, OnInit, ViewChild} from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import {MatSnackBar, MatSnackBarModule} from '@angular/material/snack-bar';
import { ZXingScannerModule } from '@zxing/ngx-scanner';
import {Subscription} from 'rxjs';
import {WebsocketService} from '../../services/websocket/websocket.service';
import {HttpClient} from '@angular/common/http';
import QRCodeDecoder from 'qrcode-decoder';
import {CommonModule} from '@angular/common';
import {MatCardModule} from '@angular/material/card';
import {environment} from '../../../environment';

@Component({
  selector: 'app-qrcode',
  imports: [CommonModule, ZXingScannerModule, MatIconModule, MatButtonModule, MatSnackBarModule, MatCardModule ],
  templateUrl: './qrcode.component.html',
  styleUrl: './qrcode.component.scss'
})
export class QrcodeComponent implements OnInit, OnDestroy {
  scannerEnabled = true;
  private scannedString: string = '';
  qrCodeImage: string | null = null;
  sendQrCodeResult: any = null;
  @ViewChild('qrImage', {static: false}) qrImage!: ElementRef<HTMLImageElement>;
  private subscriptions: Subscription[] = [];

  constructor(private websocketService: WebsocketService,
              private http: HttpClient,
              private _snackBar: MatSnackBar) {
  }

  ngOnInit() {
    this.subscriptions.push(
      this.websocketService.getQRCode().subscribe((qr: string) => this.qrCodeImage = qr)
    );

    this.subscriptions.push(
      this.websocketService.getSendQrCodeResult().subscribe((data: any) => this.sendQrCodeResult = data)
    );
  }

  ngOnDestroy() {
    this.subscriptions.forEach(sub => sub.unsubscribe());
  }

  // **QR-Code aus Bild decodieren**
  async decodeQRCode() {
    if (!this.qrImage || !this.qrImage.nativeElement || !this.qrImage.nativeElement.src) {
      this._snackBar.open('Kein QR-Code-Bild gefunden!', 'OK', { duration: 3000 });
      return;
    }

    const decoder = new QRCodeDecoder();

    try {
      const result = await decoder.decodeFromImage(this.qrImage.nativeElement);
      this.scannedString = result?.data || 'Kein QR-Code erkannt';
      this._snackBar.open(`Erkannt: ${this.scannedString}`, 'OK', { duration: 3000 });
      console.info('Decodieren des QR-Codes:', result);
      console.info('scannedString:', this.scannedString);
      this.sendQRCodeData(this.scannedString);
    } catch (error) {
      console.error('Fehler beim Decodieren des QR-Codes:', error);
      this._snackBar.open('Fehler beim Decodieren des QR-Codes', 'OK', { duration: 3000 });
    }
  }

  private apiUrl = environment.apiUrls.eventingService.qrcodeScanResult;

  sendQRCodeData(qrData: string) {
    console.info("sendQRCodeData:", qrData)
    const formData = new FormData();
    formData.append('qrdata', qrData);
    formData.append('type', 'ReadQrCode');
    console.info("sendQRCodeData formData:", formData)
    this.http.post(this.apiUrl, formData).subscribe(
      response => {
        console.log("Datei an externen Service gesendet:", response);
        this._snackBar.open('Datei erfolgreich gesendet', 'OK', { duration: 3000 });
      },
      error => {
        console.error("Fehler beim Senden an API:", error);
        this._snackBar.open('Fehler beim Senden', 'Fehler', { duration: 3000 });
      }
    );
  }

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
