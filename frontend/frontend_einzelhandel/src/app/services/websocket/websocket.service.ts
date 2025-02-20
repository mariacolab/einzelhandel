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
  private classifiedFilesubject = new Subject<any>();
  private trainingSubject = new Subject<any>();
  private sendQrCodeResultSubject = new Subject<any>();
  private socket2 = io('http://nginx:5010');
  private socket3 = io('http://nginx:5011');


  constructor() {
      this.socket = io('http://localhost:5008');

      this.socket.on('new_message', (msg: any) => {
        console.log("Neues Event erhalten:", msg);

      if (msg.type === "QRCodeGenerated") {
        this.qrCodeSubject.next(`data:image/jpg;base64,${msg.image}`);
        console.log("QR-Code generiert:", msg.image);
        }
      else if (msg.type === "ClassifiedFiles") {
        console.log("ClassifiedFiles Datei erhalten:", msg);
        this.classifiedFilesubject.next(msg);
      }
      else if (msg.type === "Trainingdata") {
        console.log("Trainingdata erhalten:", msg);
        this.trainingSubject.next(msg);
      }
      else if (msg.type === "sendQrCodeResult") {
              console.log("sendQrCodeResult erhalten:", msg);
              this.sendQrCodeResultSubject.next(msg);
      }
    });
  }

  startWatchdog() {
    this.socket2.emit('start_watchdog');
    this.socket3.emit('start_watchdog');
  }

  stopWatchdog() {
    this.socket2.emit('stop_watchdog');
    this.socket3.emit('stop_watchdog');
  }

  getQRCode(): Observable<string> {
    return this.qrCodeSubject.asObservable();
  }

  getClassifiedFiles(): Observable<any> {
    return this.classifiedFilesubject.asObservable();
  }

  getTraining(): Observable<any> {
    return this.trainingSubject.asObservable();
  }

  getSendQrCodeResult(): Observable<any> {
      return this.sendQrCodeResultSubject.asObservable();
  }
}
