import { NgIf } from '@angular/common';
import { Component, inject } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { DataService } from '../data.service';
import { MatDialog } from '@angular/material/dialog';
import {DialogContentExampleDialogComponent} from '../dialog-content-example-dialog/dialog-content-example-dialog.component';

@Component({
    selector: 'app-product-details',
    imports: [NgIf, MatFormFieldModule, MatSelectModule, MatInputModule, MatButtonModule],
    templateUrl: './product-details.component.html',
    styleUrl: './product-details.component.scss'
})
export class ProductDetailsComponent {
    constructor(private dataService: DataService) { }

    posts: any[] | undefined;
    item: any;

    public getPosts(): void {
        this.dataService.getPosts().subscribe(
            data => this.posts = data,
            error => console.error(error),
            () => console.log('Posts loaded')
        );
    }

    public getPostById(): void {
        this.dataService.getPostById(1).subscribe(
            data => this.item = data,
            error => console.error(error),
            // () => console.log('Post loaded')
            () => console.log(this.item)
        );
    }

    public classify(): string {
        return "banane";
    }

    public showDatabaseEntry(entry: string): void {
        this.getPostById();
    }

    ngOnInit(): void {
        this.showDatabaseEntry(this.classify());
    }

    readonly dialog = inject(MatDialog)
    public showDialog(): void {
        const dialogRef = this.dialog.open(DialogContentExampleDialogComponent);

        dialogRef.afterClosed().subscribe(result => {
            console.log(`Dialog result: ${result}`);
        });
    }
}
