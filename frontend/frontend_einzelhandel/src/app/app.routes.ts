import { Routes } from '@angular/router';
import { MessagesComponent } from './components/messages.component';
import { WebsocketService } from './services/websocket.service';


export const routes: Routes = [
  { path: 'messages', component: MessagesComponent },
  { path: '', redirectTo: '/messages', pathMatch: 'full' } // Default-Route
];
