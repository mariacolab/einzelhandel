// import { Component, inject } from '@angular/core';
// import { MatButtonModule } from '@angular/material/button';
// import { MatIconModule } from '@angular/material/icon';
// import { Router, RouterLink } from '@angular/router';
// import { AuthService } from '../../services/auth/auth.service';

import { Component, inject } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatGridListModule } from '@angular/material/grid-list';
import { MatIconModule } from '@angular/material/icon';
import { MatListModule } from '@angular/material/list';
import { MatSelectModule } from '@angular/material/select';
import { WebsocketService } from '../../services/websocket/websocket.service';
import { Subscription } from 'rxjs';

import { MatSnackBar } from '@angular/material/snack-bar';
import { Router, RouterModule } from '@angular/router';
import { AuthService } from '../../services/auth/auth.service';

// interface ImageCards {
//   avatar: string;
//   class: string;
// }

interface ImageCards {
  imageUrl: string;
  class: string;
}

@Component({
  selector: 'app-employee',
  // imports: [RouterLink, MatIconModule, MatButtonModule],
  imports: [MatListModule, MatIconModule, MatFormFieldModule, MatSelectModule, MatCardModule, MatButtonModule, MatGridListModule],
  templateUrl: './employee.component.html',
  styleUrl: './employee.component.scss'
})
export class EmployeeComponent {
  // imageCards: ImageCards[] = [
  //   { avatar: 'apple', class: 'Apfel' },
  //   { avatar: 'banana', class: 'Banane' },
  //   { avatar: 'cucumber', class: 'Apfel' },
  //   { avatar: 'apple', class: 'Apfel' },
  //   { avatar: 'banana', class: 'Kiwi' },
  // ];

  imageCards: ImageCards[] = [
    { imageUrl: 'https://upload.wikimedia.org/wikipedia/commons/thumb/1/15/Red_Apple.jpg/661px-Red_Apple.jpg?20151001144956', class: 'Apfel' },
    { imageUrl: 'https://upload.wikimedia.org/wikipedia/commons/7/77/Banana_d%C3%A1gua.jpg', class: 'Banane' },
    { imageUrl: 'https://upload.wikimedia.org/wikipedia/commons/8/82/Golden_Asian_Pear_2.png', class: 'Apfel' },
    { imageUrl: 'https://upload.wikimedia.org/wikipedia/commons/4/40/Bananas_on_countertop.JPG', class: 'Banane' },
    { imageUrl: 'https://upload.wikimedia.org/wikipedia/commons/d/d3/Kiwi_aka.jpg', class: 'Kiwi' },
  ];
  
  objectClasses: string[] = [
    'Apfel', 'Aubergine', 'Avocado', 'Banane', 'Birne', 'Bohnen', 'Cerealien', 'Chips', 'Essig', 'Fisch', 'Gewuerze', 'Granatapfel', 'Honig', 'Kaffee', 'Kaki', 'Karotte', 'Kartoffel', 'Kiwi', 'Knoblauch', 'Kuchen', 'Mais', 'Mandarine', 'Mango', 'Marmelade', 'Mehl', 'Milch', 'Nudeln', 'Nuss', 'Oel', 'Orange', 'Pampelmuse', 'Paprika', 'Pflaume', 'Reis', 'Saft', 'Schokolade', 'Soda', 'Suessigkeit', 'Tee', 'Tomate', 'Tomatensauce', 'Wasser', 'Zitrone', 'Zucchini', 'Zucker', 'Zwiebel'
  ];
  // selected = 'option2';

  // constructor(private websocketService: WebsocketService) {}
  websocketService = inject(WebsocketService);
  private subscription!: Subscription;
  qrCodeImage: string | null = null;
  misclassifiedFile: any = null;

  // getMessages() {
  //   console.log('getMessages()!');
  //   this.subscription = this.websocketService.getMessages().subscribe(msg => {
  //     console.log(msg);
  //     if (msg.eventType === "QRCodeGenerated") {
  //       this.qrCodeImage = `data:image/png;base64,${msg.data}`;
  //     }
  //     else if (msg.eventType === "MisclassifiedFiles") {
  //       this.misclassifiedFile = msg;
  //       // console.log(msg);
  //     }
  //   });
  // }

  authService = inject(AuthService);
  public logout() {
    this.authService.logout();
    this.router.navigate(['/login']);
  }

  snackBar = inject(MatSnackBar);
  router = inject(Router);
  reclassify() {
    this.snackBar.open('Re-classifying. Please wait...', '', { duration: 4000 });
    setTimeout(() => {
      this.snackBar.open('Done. Logging out.', '', { duration: 1000 });
    }, 4000);
    // this.router.navigate(['/product-details']);
    // setTimeout(() => {this.router.navigate(['/login'])}, 2000);
    setTimeout(() => {
      this.logout();
    }, 5000);
  }
}
