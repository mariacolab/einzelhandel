import { Component } from '@angular/core';
import {ChangeDetectionStrategy, inject} from '@angular/core';
import {MatButtonModule} from '@angular/material/button';
import {MatDialog, MatDialogModule} from '@angular/material/dialog';

@Component({
  selector: 'app-dialog-content-example-dialog',
  imports: [MatButtonModule, MatDialogModule],
  templateUrl: './dialog-content-example-dialog.component.html',
  styleUrl: './dialog-content-example-dialog.component.scss'
})
export class DialogContentExampleDialogComponent {

}
