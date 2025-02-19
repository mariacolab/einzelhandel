import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { WebsocketService } from '../../services/websocket/websocket.service';
import { Subscription } from 'rxjs';

@Component({
  selector: 'app-messages',
  standalone: true,
  templateUrl: './messages.component.html',
  styleUrls: ['./messages.component.css'],
  imports: [CommonModule]
})
export class MessagesComponent implements OnInit, OnDestroy {
  private subscriptions: Subscription[] = [];
  qrCodeImage: string | null = null;
  misclassifiedFile: any = null;
  training: any = null;

  constructor(private websocketService: WebsocketService) {}

  ngOnInit() {
    this.subscriptions.push(
      this.websocketService.getQRCode().subscribe((qr: string) => this.qrCodeImage = qr)
    );

    this.subscriptions.push(
      this.websocketService.getMisclassifiedFiles().subscribe((file: any) => this.misclassifiedFile = file)
    );

    this.subscriptions.push(
      this.websocketService.getTraining().subscribe((data: any) => this.training = data)
    );
  }

  isValidBase64Image(base64String: string): boolean {
    return base64String.startsWith("/9j/") || base64String.startsWith("iVBOR");
  }

  getMimeType(base64String: string): string {
    if (base64String.startsWith("/9j/")) {
      console.log("Trainingdata erhalten:", "image/jpeg");
      return "image/jpg";
    } else if (base64String.startsWith("iVBOR")) {
      console.log("Trainingdata erhalten:", "image/png");
      return "image/png";
    }
    return "image/jpg";
  }

  ngOnDestroy() {
    this.subscriptions.forEach(sub => sub.unsubscribe());
  }
}
