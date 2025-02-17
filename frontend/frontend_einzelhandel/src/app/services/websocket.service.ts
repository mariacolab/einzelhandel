import { Injectable, PLATFORM_ID, Inject } from '@angular/core';
import { isPlatformBrowser } from '@angular/common';
import { Observable } from 'rxjs';
import { io, Socket } from 'socket.io-client';

@Injectable({
  providedIn: 'root'
})
export class WebsocketService {
  private socket!: Socket;

  constructor(@Inject(PLATFORM_ID) private platformId: Object) {
    if (isPlatformBrowser(this.platformId)) {
      this.socket = io('http://localhost:5008'); // Verbindung nur im Browser
    }
  }

  /**
   * Empfängt Nachrichten vom WebSocket-Server
   * und gibt ein Observable zurück, das verschiedene Events verarbeitet.
   */
  getMessages(): Observable<any> {
    return new Observable(observer => {
      this.socket.on('new_message', (msg: any) => {
        console.log("Neues Event erhalten:", msg);

        if (msg.type === "QRCodeGenerated") {
          console.log("QR-Code generiert:", msg.image);
          observer.next({ eventType: msg.type, data: msg.image });
        }
        else if (msg.type === "MisclassifiedFiles") {
          console.log("Falsch klassifizierte Datei erhalten:", msg);
          observer.next({
            eventType: msg.type,
            classification: msg.classification,
            filename: msg.file.filename,
            role: msg.role,
            file: msg.file,
            product_data: msg.product_data
          });
        }
      });

      // Cleanup-Funktion bei Observable-Abbruch
      return () => {
        this.socket.disconnect();
      };
    });
  }
}
