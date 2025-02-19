import { isPlatformBrowser } from '@angular/common';
import { Injectable } from '@angular/core';
import { Observable, Subject  } from 'rxjs';
import { io, Socket } from 'socket.io-client';

@Injectable({
  providedIn: 'root'
})
export class WebsocketService {
  private socket!: Socket;
  private qrCodeSubject = new Subject<string>();
  private misclassifiedFileSubject = new Subject<any>();
  private trainingSubject = new Subject<any>();

  constructor() {
      this.socket = io('http://localhost:5008');

      this.socket.on('new_message', (msg: any) => {
        console.log("Neues Event erhalten:", msg);

      if (msg.type === "QRCodeGenerated") {
        this.qrCodeSubject.next(`data:image/jpg;base64,${msg.data}`);
        console.log("QR-Code generiert:", msg.image);
        }
      else if (msg.type === "MisclassifiedFiles") {
        console.log("MisclassifiedFiles Datei erhalten:", msg);
        this.misclassifiedFileSubject.next(msg);
      }
      else if (msg.type === "Trainingdata") {
        console.log("Trainingdata erhalten:", msg);
        this.trainingSubject.next(msg);
      }
    });
  }

  getQRCode(): Observable<string> {
    return this.qrCodeSubject.asObservable();
  }

  getMisclassifiedFiles(): Observable<any> {
    return this.misclassifiedFileSubject.asObservable();
  }

  getTraining(): Observable<any> {
    return this.trainingSubject.asObservable();
  }
}
