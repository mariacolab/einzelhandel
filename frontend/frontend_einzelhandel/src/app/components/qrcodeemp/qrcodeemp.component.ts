import {Component, ElementRef, OnDestroy, OnInit, ViewChild} from '@angular/core';
import {MatButtonModule} from '@angular/material/button';
import {MatIconModule} from '@angular/material/icon';
import {MatSnackBar} from '@angular/material/snack-bar';
import {ZXingScannerModule} from '@zxing/ngx-scanner';
import {HttpClient} from '@angular/common/http';
import {CommonModule} from '@angular/common';
import {WebsocketService} from '../../services/websocket/websocket.service';
import {Subscription} from 'rxjs';
import QRCodeDecoder from 'qrcode-decoder';



@Component({
  selector: 'app-qrcodeemp',
  imports: [CommonModule, ZXingScannerModule, MatIconModule, MatButtonModule],
  templateUrl: './qrcodeemp.component.html',
  styleUrl: './qrcodeemp.component.scss'
})
export class QrcodeempComponent implements OnInit, OnDestroy {
  qrCodeImage: string | null = null;
  sendQrCodeResult: any = null;
  @ViewChild('qrImage', {static: false}) qrImage!: ElementRef<HTMLImageElement>;
  scannerEnabled = true;
  private scannedString: string = '';
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

  isValidBase64Image(base64String: string): boolean {
    return base64String.startsWith("/9j/") || base64String.startsWith("iVBOR");
  }

  getMimeType(base64String: string): string {
    if (base64String.startsWith("/9j/")) {
      console.log("Trainingdata erhalten:", "image/jpeg");
      return "image/jpeg";
    } else if (base64String.startsWith("iVBOR")) {
      console.log("Trainingdata erhalten:", "image/png");
      return "image/png";
    }
    return "image/jpeg";
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

      this.sendQRCodeData(this.scannedString);
    } catch (error) {
      console.error('Fehler beim Decodieren des QR-Codes:', error);
      this._snackBar.open('Fehler beim Decodieren des QR-Codes', 'OK', { duration: 3000 });
    }
  }


  // **HTTP GET Request senden**
  sendQRCodeData(qrData: string) {
    const [type, produkt] = qrData.split(';'); // Annahme: QR-Code enthält "type;produkt"

    this.http.get(`/qrcode/send/result`, {params: {type, produkt}})
      .subscribe({
        next: (response: any) => {
          this.sendQrCodeResult = response;
          this._snackBar.open('QR-Code erfolgreich gesendet!', 'OK', {duration: 3000});
        },
        error: (error: any) => {
          console.error('Fehler beim Senden des QR-Codes:', error);
          this._snackBar.open('Fehler beim Senden!', 'OK', {duration: 3000});
        }
      });
  }
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
