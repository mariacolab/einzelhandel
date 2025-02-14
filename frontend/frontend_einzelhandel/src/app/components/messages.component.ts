import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { WebsocketService } from '../services/websocket.service';

@Component({
  selector: 'app-messages',
  standalone: true,
  templateUrl: './messages.component.html',
  styleUrls: ['./messages.component.css'],
  imports: [CommonModule]
})
export class MessagesComponent implements OnInit {
  qrCodeData: string | null = null;  // Hier wird das Base64-Bild gespeichert

  constructor(private websocketService: WebsocketService) {}

  ngOnInit() {
    this.websocketService.getMessages().subscribe((data: any) => {
      console.log("QR-Code Event empfangen:", data);
      if (data.image) {
        this.qrCodeData = `data:image/png;base64,${data.image}`; // Base64-Bild setzen
      }
    });
  }
}
