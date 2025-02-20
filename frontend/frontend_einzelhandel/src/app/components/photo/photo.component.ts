import { animate, state, style, transition, trigger } from '@angular/animations';
//import { NgIf, NgSwitch, NgSwitchCase } from '@angular/common';
import { NgIf, CommonModule } from '@angular/common';
import { Component, inject, OnInit, OnDestroy  } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatGridListModule } from '@angular/material/grid-list';
//import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatSnackBar } from '@angular/material/snack-bar';
//import { RouterLink } from '@angular/router';
import { WebcamImage, WebcamInitError, WebcamModule, WebcamUtil } from 'ngx-webcam';
import { Observable, Subject } from 'rxjs';
import { NgxFileDropModule, NgxFileDropEntry } from 'ngx-file-drop';
import { DataService } from '../../services/data/data.service';
import { ImageUploadComponent } from '../image_upload/image-upload.component';
//import { ProductDetailsComponent } from '../product-details/product-details.component';
import { WebsocketService } from '../../services/websocket/websocket.service';
import { Subscription } from 'rxjs';


@Component({
  selector: 'app-photo',
  imports: [CommonModule, WebcamModule, NgxFileDropModule, NgIf, MatButtonModule, MatCardModule, MatGridListModule, MatFormFieldModule, MatSelectModule, ImageUploadComponent, MatInputModule], //MatIconModule, ProductDetailsComponent, RouterLink NgSwitch, NgSwitchCase
  templateUrl: './photo.component.html',
  styleUrl: './photo.component.scss',
  animations: [
    trigger('openClose', [
      // ...
      state(
        'open',
        style({
          // height: '200px',
          opacity: 1,
          // backgroundColor: 'yellow',
        }),
      ),
      state(
        'closed',
        style({
          height: '0px',
          opacity: 0.1,
          // backgroundColor: 'blue',
        }),
      ),
      transition('open => closed', [animate('0.1s')]),
      transition('closed => open', [animate('0.1s')]),
      // ...
    ]),
    trigger('enterTrigger', [
      state('fadeIn', style({
        opacity: '1',
        // transform: 'translateY(50%)'
      })
      ),
      transition('void => *', [style({ opacity: '0' }), animate('500ms')])
    ])
  ]
})
export class PhotoComponent implements OnInit, OnDestroy {

   private subscriptions: Subscription[] = [];
      misclassifiedFile: any = null;

      constructor(private dataService: DataService, private websocketService: WebsocketService) {}

      ngOnInit() {
        this.subscriptions.push(
          this.websocketService.getClassifiedFiles().subscribe(file => this.misclassifiedFile = file)
        );

        WebcamUtil.getAvailableVideoInputs()
              .then((mediaDevices: MediaDeviceInfo[]) => {
                this.multipleWebcamsAvailable = mediaDevices && mediaDevices.length > 1;
              });
      }
      ngOnDestroy() {
        this.subscriptions.forEach(sub => sub.unsubscribe());
      }


  // toggle webcam on/off
  public showWebcam = true;
  public allowCameraSwitch = true;
  public multipleWebcamsAvailable = false;
  public deviceId!: string;
  public videoOptions: MediaTrackConstraints = {
    // width: {ideal: 1024},
    // height: {ideal: 576}
    width: { min: 640, ideal: 1024 },
    height: { min: 480, ideal: 576 }
  };
  public errors: WebcamInitError[] = [];

  // latest snapshot
  public webcamImage: WebcamImage = null!;

  // webcam snapshot trigger
  private trigger: Subject<void> = new Subject<void>();
  // switch to next / previous / specific webcam; true/false: forward/backwards, string: deviceId
  private nextWebcam: Subject<boolean | string> = new Subject<boolean | string>();

//   public ngOnInit(): void {
//     WebcamUtil.getAvailableVideoInputs()
//       .then((mediaDevices: MediaDeviceInfo[]) => {
//         this.multipleWebcamsAvailable = mediaDevices && mediaDevices.length > 1;
//       });
//   }

  public triggerSnapshot(): void {
    this.trigger.next();
    this.showWebcam = !this.showWebcam;
  }

  public handleInitError(error: WebcamInitError): void {
    this.errors.push(error);
  }

  public showNextWebcam(directionOrDeviceId: boolean | string): void {
    // true => move forward through devices
    // false => move backwards through devices
    // string => move to device with given deviceId
    this.nextWebcam.next(directionOrDeviceId);
  }

  public handleImage(webcamImage: WebcamImage): void {
    console.info('received webcam image', webcamImage);
    this.webcamImage = webcamImage;
  }

  public cameraWasSwitched(deviceId: string): void {
    console.log('active device: ' + deviceId);
    this.deviceId = deviceId;
  }

  public get triggerObservable(): Observable<void> {
    return this.trigger.asObservable();
  }

  public get nextWebcamObservable(): Observable<boolean | string> {
    return this.nextWebcam.asObservable();
  }

  snackBar = inject(MatSnackBar);
  // data: any;
  item: any;

  public imageName = 'test.jpg';
  public imageFormat = 'image/jpeg/';
  handleCapturedImage(webcamImage: WebcamImage) {
    this.webcamImage = webcamImage;
    const arr = this.webcamImage.imageAsDataUrl.split(",");
    // const mime = arr[0].match(/:(.*?);/)[1];
    const bstr = atob(arr[1]);
    let n = bstr.length;
    const u8arr = new Uint8Array(n);
    while (n--) {
      u8arr[n] = bstr.charCodeAt(n);
    }
    const file: File = new File([u8arr], this.imageName, { type: this.imageFormat })
    console.log(file);
    // return file;
    this.dataService.postformData(file).subscribe(
      data => this.item = data,
      error => {
        console.error(error);
        this.snackBar.open('Handle failed', 'Dismiss', {
          duration: 3000
        });
      },
      // () => console.log('Image posted')
      () => console.log(this.item)
    );
  }

  // public postImage(img: File): void {
  //   this.dataService.postformData(img).subscribe(
  //     data => this.item = data,
  //     error => console.error(error),
  //     () => console.log('Post loaded')
  //     // () => console.log(this.item)
  //   );
  // }

  public showProductDetails: boolean = false;
}
