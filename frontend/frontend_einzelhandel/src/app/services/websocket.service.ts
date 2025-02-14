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

  getMessages(): Observable<any> {
    return new Observable(observer => {
      this.socket.on('new_message', (msg: any) => {
        console.log("Neues Event erhalten:", msg);

        if (msg.type === "QRCodeGenerated") {
          observer.next(msg);  // Sende das Event an Subscriber (Component)
        }
      });

      return () => {
        this.socket.disconnect();
      };
    });
  }
}
