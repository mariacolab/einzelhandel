// import { NgIf } from '@angular/common';
import { Component, inject } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { DataService } from '../../services/data/data.service';
import { MatDialog } from '@angular/material/dialog';
// import {DialogContentExampleDialogComponent} from '../dialog-content-example-dialog/dialog-content-example-dialog.component';

import {MatTableModule} from '@angular/material/table';
import { Router } from '@angular/router';
import { MatCardModule } from '@angular/material/card';

// export interface PeriodicElement {
//   name: string;
//   position: number;
//   weight: number;
//   symbol: string;
// }

// const ELEMENT_DATA: PeriodicElement[] = [
//   {position: 1, name: 'Hydrogen', weight: 1.0079, symbol: 'H'},
//   {position: 2, name: 'Helium', weight: 4.0026, symbol: 'He'},
//   {position: 3, name: 'Lithium', weight: 6.941, symbol: 'Li'},
//   {position: 4, name: 'Beryllium', weight: 9.0122, symbol: 'Be'},
//   {position: 5, name: 'Boron', weight: 10.811, symbol: 'B'},
//   {position: 6, name: 'Carbon', weight: 12.0107, symbol: 'C'},
//   {position: 7, name: 'Nitrogen', weight: 14.0067, symbol: 'N'},
//   {position: 8, name: 'Oxygen', weight: 15.9994, symbol: 'O'},
//   {position: 9, name: 'Fluorine', weight: 18.9984, symbol: 'F'},
//   {position: 10, name: 'Neon', weight: 20.1797, symbol: 'Ne'},
// ];

// // export interface TableElement {
// //   classification: string;
// //   product: string;
// //   info: string;
// //   shelf: string;
// //   price_piece: number;
// //   price_kg: number;
// // }

// export interface TableElement {
//   column1: string;
//   column2: string;
// }

// const PRODUCT_DATA: TableElement[] = [
//   {column1: 'Classification', column2: 'Fruits'},
//   {column1: 'Product', column2: 'Banana'},
//   {column1: 'Info', column2: 'Brazil'},
//   {column1: 'Shelf', column2: 'Fruits 2'},
//   {column1: 'Price per piece', column2: '0.00 Euro'},
//   {column1: 'Price per kilogramme', column2: '1.29 Euro'},
// ];

@Component({
    selector: 'app-product-details',
    imports: [MatFormFieldModule, MatSelectModule, MatInputModule, MatButtonModule,MatTableModule, MatCardModule],
    templateUrl: './product-details.component.html',
    styleUrl: './product-details.component.scss'
})
export class ProductDetailsComponent {
    constructor(private dataService: DataService) { }

    // posts: any[] | undefined;
    // item: any;

    // public getPosts(): void {
    //     this.dataService.getPosts().subscribe(
    //         data => this.posts = data,
    //         error => console.error(error),
    //         () => console.log('Posts loaded')
    //     );
    // }

    // public getPostById(): void {
    //     this.dataService.getPostById(1).subscribe(
    //         data => this.item = data,
    //         error => console.error(error),
    //         // () => console.log('Post loaded')
    //         () => console.log(this.item)
    //     );
    // }

    // public classify(): string {
    //     return "banane";
    // }

    // public showDatabaseEntry(entry: string): void {
    //     this.getPostById();
    // }

    // ngOnInit(): void {
    //     this.showDatabaseEntry(this.classify());
    // }

    // readonly dialog = inject(MatDialog)
    // public showDialog(): void {
    //     const dialogRef = this.dialog.open(DialogContentExampleDialogComponent);

    //     dialogRef.afterClosed().subscribe(result => {
    //         console.log(`Dialog result: ${result}`);
    //     });
    // }

    // displayedColumns: string[] = ['position', 'name', 'weight', 'symbol'];
    // dataSource = ELEMENT_DATA;

    // columnsToDisplay = ['column1', 'column2'];
    // tableSource = PRODUCT_DATA;

    router = inject(Router);
    navigateToCustomer() {
      console.log('navigate!');
      this.router.navigate(['/customer']);
    }
}
