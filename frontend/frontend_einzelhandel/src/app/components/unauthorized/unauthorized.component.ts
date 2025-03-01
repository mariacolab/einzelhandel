import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ZXingScannerModule } from '@zxing/ngx-scanner';
import { Router } from '@angular/router';
import * as QRCode from 'qrcode';

@Component({
  selector: 'app-unauthorized',
  imports: [CommonModule, ZXingScannerModule],
  templateUrl: './unauthorized.component.html',
  styleUrls: ['./unauthorized.component.scss']
})
export class UnauthorizedComponent {
  qrCodeUrl: string = ''; // Die QR-Code-Daten (z. B. eine URL)
  scannedData: string | null = null;
  scannerEnabled = true;

  constructor(private router: Router) {
    this.generateQRCode();
  }

  // QR-Code generieren
  async generateQRCode() {
    try {
      this.qrCodeUrl = await QRCode.toDataURL('https://example.com/login'); // Hier deine URL einfügen
    } catch (err) {
      console.error('QR-Code konnte nicht generiert werden:', err);
    }
  }

  // Wenn ein QR-Code gescannt wurde
  scanSuccessHandler(event: string) {
    this.scannedData = event;
    console.log('✅ QR-Code gescannt:', event);
    this.router.navigate(['/login']); // Beispiel: Weiterleitung zur Login-Seite
  }
}
