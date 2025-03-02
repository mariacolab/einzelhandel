import { animate, state, style, transition, trigger } from '@angular/animations';
import { NgIf, CommonModule } from '@angular/common';
import {Component, inject, OnInit, OnDestroy, ViewChild, ElementRef} from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatGridListModule } from '@angular/material/grid-list';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatSnackBar } from '@angular/material/snack-bar';
import { WebcamImage, WebcamInitError, WebcamModule, WebcamUtil } from 'ngx-webcam';
import { Observable, Subject } from 'rxjs';
import { NgxFileDropModule, NgxFileDropEntry } from 'ngx-file-drop';
import { DataService } from '../../services/data/data.service';
import { ImageUploadComponent } from '../image_upload/image-upload.component';
import { WebsocketService } from '../../services/websocket/websocket.service';
import { Subscription } from 'rxjs';
import {AuthService} from '../../services/auth/auth.service';
import {HttpClient, HttpHeaders} from '@angular/common/http';
import {FormsModule} from '@angular/forms';
import {MatIconModule} from '@angular/material/icon';
import {MatOptionModule} from '@angular/material/core';
import {environment} from '../../../environment';
import * as QRCodeDecoder from 'qrcode-decoder';
import {CookieService} from 'ngx-cookie-service';


@Component({
  selector: 'app-photo',
  imports: [CommonModule, FormsModule,  WebcamModule, NgxFileDropModule, NgIf, MatButtonModule, MatCardModule, MatGridListModule, MatFormFieldModule, MatSelectModule, ImageUploadComponent, MatInputModule, MatIconModule, MatButtonModule, MatOptionModule], //MatIconModule, ProductDetailsComponent, RouterLink NgSwitch, NgSwitchCase
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
    private scannedString: string = '';
      misclassifiedFile: any = null;
      qrCodeVisible = false;
      userRole: string = '';
      classification: string = '';
      filename: string = '';
      mixed_results: string = '';
      qrCodeImage: string | null = null;
      sendQrCodeResult: any = null;
      @ViewChild('qrImage', {static: false}) qrImage!: ElementRef<HTMLImageElement>;
      showRejectionOptions: boolean = false;
      showQROptions: boolean = false;

      constructor(private authService: AuthService,
                  private dataService: DataService,
                  private websocketService: WebsocketService,
                  private http: HttpClient,
                  private _snackBar: MatSnackBar,
                  private cookieService: CookieService) {}

      ngOnInit() {
        this.authService.getUserRole().subscribe(role => {
          this.userRole = role;
          console.log("Benutzerrolle:", role);
          console.log("Rolle", this.userRole);
        });

        this.subscriptions.push(
          this.websocketService.getQRCode().subscribe((qr: string) => this.qrCodeImage = qr)
        );

        this.subscriptions.push(
          this.websocketService.getSendQrCodeResult().subscribe((data: any) => this.sendQrCodeResult = data)
        );

        const subscription = this.websocketService.getClassifiedFiles().subscribe(file => {
          if (file) {
            this.misclassifiedFile = file;

            // Assign properties to variables
            this.classification = file.classification;
            this.filename = file.filename;
            this.mixed_results = file.mixed_results;
          }
        });

        // Push the subscription properly
        this.subscriptions.push(subscription);

        WebcamUtil.getAvailableVideoInputs()
          .then((mediaDevices: MediaDeviceInfo[]) => {
            this.multipleWebcamsAvailable = mediaDevices && mediaDevices.length > 1;
          });
      }
      ngOnDestroy() {
        this.subscriptions.forEach(sub => sub.unsubscribe());
      }


  // toggle webcam on/off
  public showWebcam = false;
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

  toggleWebcam() {
    this.showWebcam = !this.showWebcam; // Webcam ein-/ausblenden
  }

  public handleImage(webcamImage: WebcamImage): void {
    console.info('received webcam image', webcamImage);
    this.webcamImage = webcamImage;
    this.showWebcam = false;
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
    this.resetState();
    this.webcamImage = webcamImage;
    const arr = this.webcamImage.imageAsDataUrl.split(",");
    const bstr = atob(arr[1]);
    let n = bstr.length;
    const u8arr = new Uint8Array(n);
    while (n--) {
      u8arr[n] = bstr.charCodeAt(n);
    }
    const file: File = new File([u8arr], this.imageName, { type: this.imageFormat })

    const formData = new FormData();
    formData.append('type', 'ProcessFiles');
    formData.append('filename', file);

    const sessionCookie = this.cookieService.get('session');
    new HttpHeaders({
      'Cookie': `session=${sessionCookie}`
    });
    this.http.post( environment.apiUrls.eventingService.imageUploaded, formData, {
      withCredentials: true
    }).subscribe(
      response => {
        console.log("Datei an externen Service gesendet:", response);
        this.snackBar.open('Datei erfolgreich gesendet', 'OK', { duration: 3000 });
      },
      error => {
        console.error("Fehler beim Senden an API:", error);
        this.snackBar.open('Fehler beim Senden', 'Fehler', { duration: 3000 });
      }
    );
  }

  //von Maria Schuster
  confirm() {
    this.showRejectionOptions = true;
    console.log(this.showRejectionOptions)
    console.log('Bestätigung ausgeführt.');
    setTimeout(() => {
      this.showQROptions = true;
    }, 3000);
  }

  reject() {
    this.showRejectionOptions = false;
    console.log('Ablehnung ausgeführt. Bitte neue Klassifizierung auswählen.');
  }

  sendData() {
    const formData = new FormData();
    formData.append('is_classification_correct', this.showRejectionOptions.toString());
    formData.append('classification', this.misclassifiedFile.classification);
    formData.append('type', "CorrectedFiles");
    formData.append('filename', this.misclassifiedFile.filename);
    formData.append('mixed_results', this.misclassifiedFile.mixed_results);
    console.log('Erfolgreiche Antwort:', this.showRejectionOptions.toString())
    // Mit withCredentials werden vorhandene Cookies (z. B. die Session) automatisch mitgesendet.
    this.http.post(environment.apiUrls.eventingService.publishCorrectedClassification, formData, { withCredentials: true })
      .subscribe(
        response => {
          console.log('Erfolgreiche Antwort:', response);
        },
        error => {
          console.error('Fehler beim Absenden:', error);
        }
      );
    this.qrCodeVisible = true;
  }

  /*async decodeQRCode() {
    if (!this.qrImage || !this.qrImage.nativeElement || !this.qrImage.nativeElement.src) {
      this._snackBar.open('Kein QR-Code-Bild gefunden!', 'OK', { duration: 3000 });
      return;
    }

    const decoder = new QRCodeDecoder();

    try {
      const result = await decoder.decodeFromImage(this.qrImage.nativeElement);
      this.scannedString = result?.data || 'Kein QR-Code erkannt';
      this._snackBar.open(`Erkannt: ${this.scannedString}`, 'OK', { duration: 3000 });
      console.info('Decodieren des QR-Codes:', result);
      console.info('scannedString:', this.scannedString);
      this.sendQRCodeData(this.scannedString);
    } catch (error) {
      console.error('Fehler beim Decodieren des QR-Codes:', error);
      this._snackBar.open('Fehler beim Decodieren des QR-Codes', 'OK', { duration: 3000 });
    }
  }*/

  async decodeQRCode() {
    if (!this.qrImage || !this.qrImage.nativeElement || !this.qrImage.nativeElement.src) {
      this._snackBar.open('Kein QR-Code-Bild gefunden!', 'OK', { duration: 3000 });
      return;
    }
    console.log('QRCodeDecoder:', QRCodeDecoder);
    const decoder = new QRCodeDecoder.default();

    try {
      const result = await decoder.decodeFromImage(this.qrImage.nativeElement);
      this.scannedString = result?.data || 'Kein QR-Code erkannt';

      if (!this.scannedString.startsWith('http')) {
        this._snackBar.open('Kein gültiger URL-QR-Code erkannt', 'OK', { duration: 3000 });
        return;
      }

      this._snackBar.open(`Erkannte URL: ${this.scannedString}`, 'OK', { duration: 3000 });
      console.info('Decodierte QR-Code-URL:', this.scannedString);

      //Direkt die erkannte URL aufrufen
      window.open(this.scannedString, '_blank'); // Öffnet die URL in einem neuen Tab
    } catch (error) {
      console.error('Fehler beim Decodieren des QR-Codes:', error);
      this._snackBar.open('Fehler beim Decodieren des QR-Codes', 'OK', { duration: 3000 });
    }
  }



  private apiUrl = environment.apiUrls.eventingService.qrcodeScanResult;

  sendQRCodeData(qrData: string) {
    console.info("sendQRCodeData:", qrData)
    const formData = new FormData();
    formData.append('qrdata', qrData);
    formData.append('type', 'ReadQrCode');
    console.info("sendQRCodeData formData:", formData)
    this.http.post(this.apiUrl, formData).subscribe(
      response => {
        console.log("Datei an externen Service gesendet:", response);
        this._snackBar.open('Datei erfolgreich gesendet', 'OK', { duration: 3000 });
      },
      error => {
        console.error("Fehler beim Senden an API:", error);
        this._snackBar.open('Fehler beim Senden', 'Fehler', { duration: 3000 });
      }
    );
  }

  resetState(): void {
    // Webcam-Zustände
    this.showWebcam = false;
    this.webcamImage = null!;

    // Fehlklassifizierte Datei und zugehörige Daten
    this.misclassifiedFile = null;
    this.classification = '';
    this.filename = '';
    this.mixed_results = '';

    // QR-Code-bezogene Variablen
    this.qrCodeVisible = false;
    this.sendQrCodeResult = null;

    // Anzeige-Flags
    this.showRejectionOptions = false;
    this.showQROptions = false;

  }


  public showProductDetails: boolean = false;
}
