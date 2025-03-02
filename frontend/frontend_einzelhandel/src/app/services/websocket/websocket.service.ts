//von Maria Schuster
import { isPlatformBrowser } from '@angular/common';
import { Injectable } from '@angular/core';
import { Observable, Subject  } from 'rxjs';
import { io, Socket } from 'socket.io-client';
import {environment} from '../../../environment';

@Injectable({
  providedIn: 'root'
})

export class WebsocketService {
  socket!: Socket;
  private socketTF!: Socket;
  private qrCodeSubject = new Subject<string>();
  private classifiedFilesubject = new Subject<any>();
  private sendQrCodeResultSubject = new Subject<any>();
  private labeledTrainingAckSubject = new Subject<any>();
  private trainingSubjectTF = new Subject<any>();

  constructor() {
      this.socket = io(environment.apiUrls.externalServices.service5008, {
        transports: ['websocket']
      });

      this.socketTF = io(environment.apiUrls.externalServices.service5015, {
        //path: "/socket-tf/",
        transports: ['websocket']
      });


      this.socketTF.on('connect', () => {
        console.log('TF Verbindung erfolgreich mit WebSockets!');
      });

      this.socketTF.on('connect_error', (error: any) => {
        console.error('TF WebSocket-Verbindungsfehler:', error);
      });

      this.socketTF.on('disconnect', () => {
        console.log('TF WebSocket-Verbindung getrennt.');
      });

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

      else if (msg.type === "sendQrCodeResult") {
        console.log("sendQrCodeResult erhalten:", msg);
        this.sendQrCodeResultSubject.next(msg);
      }

      this.socketTF.on('Trainingdata', (msg: any) => {
        console.log("Trainingdata (TF) erhalten:", msg);
        this.trainingSubjectTF.next(msg);
      });

      // Empfang der Bestätigung nach dem Labeln
      this.socketTF.on('LabeledTrainingdataAck', (msg: any) => {
        console.log("LabeledTrainingdataAck received:", msg);
        this.labeledTrainingAckSubject.next(msg);
      });
    });
  }

  ngOnInit(){
    console.log('WebSocket Service wird verbunden. Verbindungen werden geöffnet.');
    this.socketTF.connect();
  }

  ngOnDestroy() {
    console.log(' WebSocket Service wird zerstört. Verbindungen werden geschlossen.');
    this.socketTF.disconnect();
  }

  // Observable für Empfang der Acknowledgment-Nachricht
  getLabeledTrainingAck(): Observable<any> {
    return this.labeledTrainingAckSubject.asObservable();
  }

  // Sendet das LabeledTrainingdata-Event mit den Labels
  sendLabeledTrainingDataTf(data: any) {
    this.socketTF.emit("LabeledTrainingdata", data);
  }
  getQRCode(): Observable<string> {
    return this.qrCodeSubject.asObservable();
  }

  getClassifiedFiles(): Observable<any> {
    return this.classifiedFilesubject.asObservable();
  }

  getTrainingDataTF(): Observable<any> {
    return this.trainingSubjectTF.asObservable();
  }

  getSendQrCodeResult(): Observable<any> {
      return this.sendQrCodeResultSubject.asObservable();
  }
}
