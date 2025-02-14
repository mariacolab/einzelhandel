import { NgIf } from '@angular/common';
import { Component, inject } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatGridListModule } from '@angular/material/grid-list';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatSnackBar } from '@angular/material/snack-bar';
import { WebcamImage, WebcamInitError, WebcamModule, WebcamUtil } from 'ngx-webcam';
import { Observable, Subject } from 'rxjs';
import { DataService } from '../data.service';
import { ProductDetailsComponent } from '../product-details/product-details.component';
import { Router, RouterLink } from '@angular/router';

@Component({
    selector: 'app-photo',
    imports: [MatIconModule, WebcamModule, NgIf, MatButtonModule, MatCardModule, MatGridListModule, MatFormFieldModule, MatSelectModule, MatInputModule, ProductDetailsComponent, RouterLink],
    templateUrl: './photo.component.html',
    styleUrl: './photo.component.scss'
})
export class PhotoComponent {
    // toggle webcam on/off
    public showWebcam = true;
    public showImage = false;
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

    public ngOnInit(): void {
        WebcamUtil.getAvailableVideoInputs()
            .then((mediaDevices: MediaDeviceInfo[]) => {
                this.multipleWebcamsAvailable = mediaDevices && mediaDevices.length > 1;
            });
    }

    public triggerSnapshot(): void {
        this.trigger.next();
        // this.showWebcam = false;
        this.showWebcam = !this.showWebcam;
        this.showImage = !this.showImage;
    }

    public toggleWebcam(): void {
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

    constructor(private dataService: DataService) { }
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

    qrResultString: string | undefined;
}
