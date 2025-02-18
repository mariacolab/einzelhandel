import { Component } from '@angular/core';

import { DataService } from '../data.service';

@Component({
  selector: 'app-data',
  imports: [],
  templateUrl: './data.component.html',
  styleUrl: './data.component.scss'
})
export class DataComponent {

  posts: any[] | undefined;
  item: any;
  data: any;

  qrResultString: string | undefined;

  constructor(private dataService: DataService) {}

  async ngOnInit() {
    this.dataService.getPosts().subscribe(
      data => this.posts = data,
      error => console.error(error),
      () => console.log('Posts loaded')
    );

    this.dataService.getPostById(1).subscribe(
      data => this.item = data,
      error => console.error(error),
      () => console.log('Post loaded')
      // () => console.log(this.item)
    );
  }
}
