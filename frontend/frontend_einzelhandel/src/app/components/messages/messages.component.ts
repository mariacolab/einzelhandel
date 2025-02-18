import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { WebsocketService } from '../services/websocket.service';
import { Subscription } from 'rxjs';

@Component({
  selector: 'app-messages',
  standalone: true,
  templateUrl: './messages.component.html',
  styleUrls: ['./messages.component.css'],
  imports: [CommonModule]
})
export class MessagesComponent implements OnInit, OnDestroy {
  private subscription!: Subscription;
  qrCodeImage: string | null = null;
  misclassifiedFile: any = null;

  constructor(private websocketService: WebsocketService) {}

  ngOnInit() {
    this.subscription = this.websocketService.getMessages().subscribe(msg => {
      if (msg.eventType === "QRCodeGenerated") {
        this.qrCodeImage = `data:image/png;base64,${msg.data}`;
      }
      else if (msg.eventType === "MisclassifiedFiles") {
        this.misclassifiedFile = msg;
      }
    });
  }

  ngOnDestroy() {
    if (this.subscription) {
      this.subscription.unsubscribe();
    }
  }
}
