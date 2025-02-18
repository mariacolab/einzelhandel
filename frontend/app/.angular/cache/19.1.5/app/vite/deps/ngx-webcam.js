import {
  CommonModule,
  NgIf
} from "./chunk-556KATUP.js";
import {
  Component,
  EventEmitter,
  Input,
  NgModule,
  Output,
  ViewChild,
  setClassMetadata,
  ɵɵadvance,
  ɵɵclassMap,
  ɵɵdefineComponent,
  ɵɵdefineInjector,
  ɵɵdefineNgModule,
  ɵɵelement,
  ɵɵelementEnd,
  ɵɵelementStart,
  ɵɵgetCurrentView,
  ɵɵlistener,
  ɵɵloadQuery,
  ɵɵnextContext,
  ɵɵproperty,
  ɵɵqueryRefresh,
  ɵɵresetView,
  ɵɵrestoreView,
  ɵɵtemplate,
  ɵɵviewQuery
} from "./chunk-IYE42FHU.js";
import "./chunk-LBBSG2YE.js";
import "./chunk-WSXI74FV.js";
import "./chunk-NGNUV6BG.js";

// node_modules/ngx-webcam/fesm2020/ngx-webcam.mjs
var _c0 = ["video"];
var _c1 = ["canvas"];
function WebcamComponent_div_3_Template(rf, ctx) {
  if (rf & 1) {
    const _r2 = ɵɵgetCurrentView();
    ɵɵelementStart(0, "div", 6);
    ɵɵlistener("click", function WebcamComponent_div_3_Template_div_click_0_listener() {
      ɵɵrestoreView(_r2);
      const ctx_r2 = ɵɵnextContext();
      return ɵɵresetView(ctx_r2.rotateVideoInput(true));
    });
    ɵɵelementEnd();
  }
}
var WebcamImage = class _WebcamImage {
  constructor(imageAsDataUrl, mimeType, imageData) {
    this._mimeType = null;
    this._imageAsBase64 = null;
    this._imageAsDataUrl = null;
    this._imageData = null;
    this._mimeType = mimeType;
    this._imageAsDataUrl = imageAsDataUrl;
    this._imageData = imageData;
  }
  /**
   * Extracts the Base64 data out of the given dataUrl.
   * @param dataUrl the given dataUrl
   * @param mimeType the mimeType of the data
   */
  static getDataFromDataUrl(dataUrl, mimeType) {
    return dataUrl.replace(`data:${mimeType};base64,`, "");
  }
  /**
   * Get the base64 encoded image data
   * @returns base64 data of the image
   */
  get imageAsBase64() {
    return this._imageAsBase64 ? this._imageAsBase64 : this._imageAsBase64 = _WebcamImage.getDataFromDataUrl(this._imageAsDataUrl, this._mimeType);
  }
  /**
   * Get the encoded image as dataUrl
   * @returns the dataUrl of the image
   */
  get imageAsDataUrl() {
    return this._imageAsDataUrl;
  }
  /**
   * Get the ImageData object associated with the canvas' 2d context.
   * @returns the ImageData of the canvas's 2d context.
   */
  get imageData() {
    return this._imageData;
  }
};
var WebcamUtil = class {
  /**
   * Lists available videoInput devices
   * @returns a list of media device info.
   */
  static getAvailableVideoInputs() {
    if (!navigator.mediaDevices || !navigator.mediaDevices.enumerateDevices) {
      return Promise.reject("enumerateDevices() not supported.");
    }
    return new Promise((resolve, reject) => {
      navigator.mediaDevices.enumerateDevices().then((devices) => {
        resolve(devices.filter((device) => device.kind === "videoinput"));
      }).catch((err) => {
        reject(err.message || err);
      });
    });
  }
};
var WebcamComponent = class _WebcamComponent {
  constructor() {
    this.width = 640;
    this.height = 480;
    this.videoOptions = _WebcamComponent.DEFAULT_VIDEO_OPTIONS;
    this.allowCameraSwitch = true;
    this.captureImageData = false;
    this.imageType = _WebcamComponent.DEFAULT_IMAGE_TYPE;
    this.imageQuality = _WebcamComponent.DEFAULT_IMAGE_QUALITY;
    this.imageCapture = new EventEmitter();
    this.initError = new EventEmitter();
    this.imageClick = new EventEmitter();
    this.cameraSwitched = new EventEmitter();
    this.availableVideoInputs = [];
    this.videoInitialized = false;
    this.activeVideoInputIndex = -1;
    this.mediaStream = null;
    this.activeVideoSettings = null;
  }
  /**
   * If the given Observable emits, an image will be captured and emitted through 'imageCapture' EventEmitter
   */
  set trigger(trigger) {
    if (this.triggerSubscription) {
      this.triggerSubscription.unsubscribe();
    }
    this.triggerSubscription = trigger.subscribe(() => {
      this.takeSnapshot();
    });
  }
  /**
   * If the given Observable emits, the active webcam will be switched to the one indicated by the emitted value.
   * @param switchCamera Indicates which webcam to switch to
   *   true: cycle forwards through available webcams
   *   false: cycle backwards through available webcams
   *   string: activate the webcam with the given id
   */
  set switchCamera(switchCamera) {
    if (this.switchCameraSubscription) {
      this.switchCameraSubscription.unsubscribe();
    }
    this.switchCameraSubscription = switchCamera.subscribe((value) => {
      if (typeof value === "string") {
        this.switchToVideoInput(value);
      } else {
        this.rotateVideoInput(value !== false);
      }
    });
  }
  /**
   * Get MediaTrackConstraints to request streaming the given device
   * @param deviceId
   * @param baseMediaTrackConstraints base constraints to merge deviceId-constraint into
   * @returns
   */
  static getMediaConstraintsForDevice(deviceId, baseMediaTrackConstraints) {
    const result = baseMediaTrackConstraints ? baseMediaTrackConstraints : this.DEFAULT_VIDEO_OPTIONS;
    if (deviceId) {
      result.deviceId = {
        exact: deviceId
      };
    }
    return result;
  }
  /**
   * Tries to harvest the deviceId from the given mediaStreamTrack object.
   * Browsers populate this object differently; this method tries some different approaches
   * to read the id.
   * @param mediaStreamTrack
   * @returns deviceId if found in the mediaStreamTrack
   */
  static getDeviceIdFromMediaStreamTrack(mediaStreamTrack) {
    if (mediaStreamTrack.getSettings && mediaStreamTrack.getSettings() && mediaStreamTrack.getSettings().deviceId) {
      return mediaStreamTrack.getSettings().deviceId;
    } else if (mediaStreamTrack.getConstraints && mediaStreamTrack.getConstraints() && mediaStreamTrack.getConstraints().deviceId) {
      const deviceIdObj = mediaStreamTrack.getConstraints().deviceId;
      return _WebcamComponent.getValueFromConstrainDOMString(deviceIdObj);
    }
  }
  /**
   * Tries to harvest the facingMode from the given mediaStreamTrack object.
   * Browsers populate this object differently; this method tries some different approaches
   * to read the value.
   * @param mediaStreamTrack
   * @returns facingMode if found in the mediaStreamTrack
   */
  static getFacingModeFromMediaStreamTrack(mediaStreamTrack) {
    if (mediaStreamTrack) {
      if (mediaStreamTrack.getSettings && mediaStreamTrack.getSettings() && mediaStreamTrack.getSettings().facingMode) {
        return mediaStreamTrack.getSettings().facingMode;
      } else if (mediaStreamTrack.getConstraints && mediaStreamTrack.getConstraints() && mediaStreamTrack.getConstraints().facingMode) {
        const facingModeConstraint = mediaStreamTrack.getConstraints().facingMode;
        return _WebcamComponent.getValueFromConstrainDOMString(facingModeConstraint);
      }
    }
  }
  /**
   * Determines whether the given mediaStreamTrack claims itself as user facing
   * @param mediaStreamTrack
   */
  static isUserFacing(mediaStreamTrack) {
    const facingMode = _WebcamComponent.getFacingModeFromMediaStreamTrack(mediaStreamTrack);
    return facingMode ? "user" === facingMode.toLowerCase() : false;
  }
  /**
   * Extracts the value from the given ConstrainDOMString
   * @param constrainDOMString
   */
  static getValueFromConstrainDOMString(constrainDOMString) {
    if (constrainDOMString) {
      if (constrainDOMString instanceof String) {
        return String(constrainDOMString);
      } else if (Array.isArray(constrainDOMString) && Array(constrainDOMString).length > 0) {
        return String(constrainDOMString[0]);
      } else if (typeof constrainDOMString === "object") {
        if (constrainDOMString["exact"]) {
          return String(constrainDOMString["exact"]);
        } else if (constrainDOMString["ideal"]) {
          return String(constrainDOMString["ideal"]);
        }
      }
    }
    return null;
  }
  ngAfterViewInit() {
    this.detectAvailableDevices().then(() => {
      this.switchToVideoInput(null);
    }).catch((err) => {
      this.initError.next({
        message: err
      });
      this.switchToVideoInput(null);
    });
  }
  ngOnDestroy() {
    this.stopMediaTracks();
    this.unsubscribeFromSubscriptions();
  }
  /**
   * Takes a snapshot of the current webcam's view and emits the image as an event
   */
  takeSnapshot() {
    const _video = this.nativeVideoElement;
    const dimensions = {
      width: this.width,
      height: this.height
    };
    if (_video.videoWidth) {
      dimensions.width = _video.videoWidth;
      dimensions.height = _video.videoHeight;
    }
    const _canvas = this.canvas.nativeElement;
    _canvas.width = dimensions.width;
    _canvas.height = dimensions.height;
    const context2d = _canvas.getContext("2d");
    context2d.drawImage(_video, 0, 0);
    const mimeType = this.imageType ? this.imageType : _WebcamComponent.DEFAULT_IMAGE_TYPE;
    const quality = this.imageQuality ? this.imageQuality : _WebcamComponent.DEFAULT_IMAGE_QUALITY;
    const dataUrl = _canvas.toDataURL(mimeType, quality);
    let imageData = null;
    if (this.captureImageData) {
      imageData = context2d.getImageData(0, 0, _canvas.width, _canvas.height);
    }
    this.imageCapture.next(new WebcamImage(dataUrl, mimeType, imageData));
  }
  /**
   * Switches to the next/previous video device
   * @param forward
   */
  rotateVideoInput(forward) {
    if (this.availableVideoInputs && this.availableVideoInputs.length > 1) {
      const increment = forward ? 1 : this.availableVideoInputs.length - 1;
      const nextInputIndex = (this.activeVideoInputIndex + increment) % this.availableVideoInputs.length;
      this.switchToVideoInput(this.availableVideoInputs[nextInputIndex].deviceId);
    }
  }
  /**
   * Switches the camera-view to the specified video device
   */
  switchToVideoInput(deviceId) {
    this.videoInitialized = false;
    this.stopMediaTracks();
    this.initWebcam(deviceId, this.videoOptions);
  }
  /**
   * Event-handler for video resize event.
   * Triggers Angular change detection so that new video dimensions get applied
   */
  videoResize() {
  }
  get videoWidth() {
    const videoRatio = this.getVideoAspectRatio();
    return Math.min(this.width, this.height * videoRatio);
  }
  get videoHeight() {
    const videoRatio = this.getVideoAspectRatio();
    return Math.min(this.height, this.width / videoRatio);
  }
  get videoStyleClasses() {
    let classes = "";
    if (this.isMirrorImage()) {
      classes += "mirrored ";
    }
    return classes.trim();
  }
  get nativeVideoElement() {
    return this.video.nativeElement;
  }
  /**
   * Returns the video aspect ratio of the active video stream
   */
  getVideoAspectRatio() {
    const videoElement = this.nativeVideoElement;
    if (videoElement.videoWidth && videoElement.videoWidth > 0 && videoElement.videoHeight && videoElement.videoHeight > 0) {
      return videoElement.videoWidth / videoElement.videoHeight;
    }
    return this.width / this.height;
  }
  /**
   * Init webcam live view
   */
  initWebcam(deviceId, userVideoTrackConstraints) {
    const _video = this.nativeVideoElement;
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
      const videoTrackConstraints = _WebcamComponent.getMediaConstraintsForDevice(deviceId, userVideoTrackConstraints);
      navigator.mediaDevices.getUserMedia({
        video: videoTrackConstraints
      }).then((stream) => {
        this.mediaStream = stream;
        _video.srcObject = stream;
        _video.play();
        this.activeVideoSettings = stream.getVideoTracks()[0].getSettings();
        const activeDeviceId = _WebcamComponent.getDeviceIdFromMediaStreamTrack(stream.getVideoTracks()[0]);
        this.cameraSwitched.next(activeDeviceId);
        this.detectAvailableDevices().then(() => {
          this.activeVideoInputIndex = activeDeviceId ? this.availableVideoInputs.findIndex((mediaDeviceInfo) => mediaDeviceInfo.deviceId === activeDeviceId) : -1;
          this.videoInitialized = true;
        }).catch(() => {
          this.activeVideoInputIndex = -1;
          this.videoInitialized = true;
        });
      }).catch((err) => {
        this.initError.next({
          message: err.message,
          mediaStreamError: err
        });
      });
    } else {
      this.initError.next({
        message: "Cannot read UserMedia from MediaDevices."
      });
    }
  }
  getActiveVideoTrack() {
    return this.mediaStream ? this.mediaStream.getVideoTracks()[0] : null;
  }
  isMirrorImage() {
    if (!this.getActiveVideoTrack()) {
      return false;
    }
    {
      let mirror = "auto";
      if (this.mirrorImage) {
        if (typeof this.mirrorImage === "string") {
          mirror = String(this.mirrorImage).toLowerCase();
        } else {
          if (this.mirrorImage.x) {
            mirror = this.mirrorImage.x.toLowerCase();
          }
        }
      }
      switch (mirror) {
        case "always":
          return true;
        case "never":
          return false;
      }
    }
    return _WebcamComponent.isUserFacing(this.getActiveVideoTrack());
  }
  /**
   * Stops all active media tracks.
   * This prevents the webcam from being indicated as active,
   * even if it is no longer used by this component.
   */
  stopMediaTracks() {
    if (this.mediaStream && this.mediaStream.getTracks) {
      this.nativeVideoElement.pause();
      this.mediaStream.getTracks().forEach((track) => track.stop());
    }
  }
  /**
   * Unsubscribe from all open subscriptions
   */
  unsubscribeFromSubscriptions() {
    if (this.triggerSubscription) {
      this.triggerSubscription.unsubscribe();
    }
    if (this.switchCameraSubscription) {
      this.switchCameraSubscription.unsubscribe();
    }
  }
  /**
   * Reads available input devices
   */
  detectAvailableDevices() {
    return new Promise((resolve, reject) => {
      WebcamUtil.getAvailableVideoInputs().then((devices) => {
        this.availableVideoInputs = devices;
        resolve(devices);
      }).catch((err) => {
        this.availableVideoInputs = [];
        reject(err);
      });
    });
  }
};
WebcamComponent.DEFAULT_VIDEO_OPTIONS = {
  facingMode: "environment"
};
WebcamComponent.DEFAULT_IMAGE_TYPE = "image/jpeg";
WebcamComponent.DEFAULT_IMAGE_QUALITY = 0.92;
WebcamComponent.ɵfac = function WebcamComponent_Factory(__ngFactoryType__) {
  return new (__ngFactoryType__ || WebcamComponent)();
};
WebcamComponent.ɵcmp = ɵɵdefineComponent({
  type: WebcamComponent,
  selectors: [["webcam"]],
  viewQuery: function WebcamComponent_Query(rf, ctx) {
    if (rf & 1) {
      ɵɵviewQuery(_c0, 7);
      ɵɵviewQuery(_c1, 7);
    }
    if (rf & 2) {
      let _t;
      ɵɵqueryRefresh(_t = ɵɵloadQuery()) && (ctx.video = _t.first);
      ɵɵqueryRefresh(_t = ɵɵloadQuery()) && (ctx.canvas = _t.first);
    }
  },
  inputs: {
    width: "width",
    height: "height",
    videoOptions: "videoOptions",
    allowCameraSwitch: "allowCameraSwitch",
    mirrorImage: "mirrorImage",
    captureImageData: "captureImageData",
    imageType: "imageType",
    imageQuality: "imageQuality",
    trigger: "trigger",
    switchCamera: "switchCamera"
  },
  outputs: {
    imageCapture: "imageCapture",
    initError: "initError",
    imageClick: "imageClick",
    cameraSwitched: "cameraSwitched"
  },
  standalone: false,
  decls: 6,
  vars: 7,
  consts: [["video", ""], ["canvas", ""], [1, "webcam-wrapper", 3, "click"], ["autoplay", "", "muted", "", "playsinline", "", 3, "resize", "width", "height"], ["class", "camera-switch", 3, "click", 4, "ngIf"], [3, "width", "height"], [1, "camera-switch", 3, "click"]],
  template: function WebcamComponent_Template(rf, ctx) {
    if (rf & 1) {
      const _r1 = ɵɵgetCurrentView();
      ɵɵelementStart(0, "div", 2);
      ɵɵlistener("click", function WebcamComponent_Template_div_click_0_listener() {
        ɵɵrestoreView(_r1);
        return ɵɵresetView(ctx.imageClick.next());
      });
      ɵɵelementStart(1, "video", 3, 0);
      ɵɵlistener("resize", function WebcamComponent_Template_video_resize_1_listener() {
        ɵɵrestoreView(_r1);
        return ɵɵresetView(ctx.videoResize());
      });
      ɵɵelementEnd();
      ɵɵtemplate(3, WebcamComponent_div_3_Template, 1, 0, "div", 4);
      ɵɵelement(4, "canvas", 5, 1);
      ɵɵelementEnd();
    }
    if (rf & 2) {
      ɵɵadvance();
      ɵɵclassMap(ctx.videoStyleClasses);
      ɵɵproperty("width", ctx.videoWidth)("height", ctx.videoHeight);
      ɵɵadvance(2);
      ɵɵproperty("ngIf", ctx.allowCameraSwitch && ctx.availableVideoInputs.length > 1 && ctx.videoInitialized);
      ɵɵadvance();
      ɵɵproperty("width", ctx.width)("height", ctx.height);
    }
  },
  dependencies: [NgIf],
  styles: [".webcam-wrapper[_ngcontent-%COMP%]{display:inline-block;position:relative;line-height:0}.webcam-wrapper[_ngcontent-%COMP%]   video.mirrored[_ngcontent-%COMP%]{transform:scaleX(-1)}.webcam-wrapper[_ngcontent-%COMP%]   canvas[_ngcontent-%COMP%]{display:none}.webcam-wrapper[_ngcontent-%COMP%]   .camera-switch[_ngcontent-%COMP%]{background-color:#0000001a;background-image:url(data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEAAAABACAYAAACqaXHeAAAE9UlEQVR42u2aT2hdRRTGf+cRQqghSqihdBFDkRISK2KDfzDWxHaRQHEhaINKqa1gKQhd6EZLN+IidCH+Q0oWIkVRC21BQxXRitVaSbKoJSGtYGoK2tQ/tU1jY5v0c5F54Xl7b/KSO/PyEt+3e5f75p7zzZwzZ74zUEIJJfyfYaEGllQGVAGZlENdBy6Z2cSiYFTSKkkfS/pH/nBF0kFJdUW9AiRVASeAukD8DgNrzOySrwEzng18KaDzALXuG8W3AiStAvqBisBRNg40mtlPxbYCOgvgPO4bncWW+JpVeDQXRQhIygDfA00F5r0XuNfMrgclQFI98DDQCNQA5ZFXqoCWBVp8XwHRHeEqcN7loy/NbHBesyqpQ1KfFj/6nC+ZvFaApFrgPaCZpYVvgCfNbDiRAElNwGFg+RIt/X8H2s2s9wYCJDUAR4HqJX7++RN40MwGpgmQVAH0AQ2BPz4AHHPl8nBOAqtyFWQjsA6oL4Ada81sPDv7uwImod8kvSJp9RyS8O2SXnb/DYVd2Y9VSroQ4ANXJO2WVJmixqh0kzMWwL4LkiqRtDnA4D1zmfE8j9g9AezcnAHaPcfXdbfdnPZ2Yps6+DwAvO/Z1naTdApY7Xng48BDZnY1MpMVQBuw3iXc5Tnb0wBwBPjUzP6eoezuArZ6svM0geJLkvZEYnl3nkntoqROSbckSW2Suj3ZOIangc7GPJuUtNGdFIfmMeavktoSSKiW9LMPw30Q8JqkekmjCbOZRhuclLQjgYSNxUBAj6RyZ9ATgUJpUtJTCSR8vpAEXHAyWK5BXYFIGHOlepSAloUk4NEYgyoknQhEwhFJ0e8h6VSaQeerCb5uZgdi9utxYBNwOUD93hIVXswM4INCi6K9wAszFC2DwLOBDjHbYp59karIUnRdzYy/3ClqVklaUhfwTICj7K25OqA7a4wWagVsm4Me/xzwg2cCqqONFzO7DPxSCAJi436GUBgHHguQD2oTlJ55oSzP9ybccsttSJw1szdjFOSnI/8dTCGZHwcORp4Nx7y3B1iZ8/sm4MW8/Euxg5wIsS/HaAp3zeP4/G7obRDXI4jiTIA22H7Xdc7X+S3A5lC7QBQ357aq3VAjCeSkwUfAJrfvz+R8A9ADLAtZB+TinpjC5JMA+//jwPZZnF8G7J+L8z4IWB/zbG+gIujVWfLBW/NStVMmqaG4POJRsIjix7h8IGnLQuoBbQki5sVAJHyYm7YkNaRRtXwQ8G1cHpX0iKRrgUjYno17Sf0LrQhJUkdCeHWkVITGJI0k1QeS3ikGSUzOyJUJJNznYneuOCnpTldcxa2kP3xJYqOeSDjqZG8ShJLnE8TTuMS6Iyu1BW7djZqkfo9N0QOuYJmYQddfB7RG+gLTNzqAY9FrL+5/nwEbvDdJJe3zzOrhNP3AWRqmk55t3ZcBuj3b2gb0Sbrbo/NNzk7fFzu7s/E5EiC+rrmeQU0Kx2skvRFoOx2ZzlmSdgbsw49JetvtBpk8nM64d/cGbNtJ0s7cGyJlwHeEv+t3nqnLSgPAUOSGyG3AHUxdzqoJbEcvcL+ZTeTeEapzJKxgaeOcc/7Mf06D7kFrguS0VDAMtGadv+E47DT9tcChJej8ISfpD+abgTe45uOkFi8mnQ+JBVQ+d4VXuOptjavcyot8pq86mfwk8LWZnaOEEkoooYQSSojDv8AhQNeGfe0jAAAAAElFTkSuQmCC);background-repeat:no-repeat;border-radius:5px;position:absolute;right:13px;top:10px;height:48px;width:48px;background-size:80%;cursor:pointer;background-position:center;transition:background-color .2s ease}.webcam-wrapper[_ngcontent-%COMP%]   .camera-switch[_ngcontent-%COMP%]:hover{background-color:#0000002e}"]
});
(() => {
  (typeof ngDevMode === "undefined" || ngDevMode) && setClassMetadata(WebcamComponent, [{
    type: Component,
    args: [{
      selector: "webcam",
      template: '<div class="webcam-wrapper" (click)="imageClick.next();">\r\n  <video #video [width]="videoWidth" [height]="videoHeight" [class]="videoStyleClasses" autoplay muted playsinline (resize)="videoResize()"></video>\r\n  <div class="camera-switch" *ngIf="allowCameraSwitch && availableVideoInputs.length > 1 && videoInitialized" (click)="rotateVideoInput(true)"></div>\r\n  <canvas #canvas [width]="width" [height]="height"></canvas>\r\n</div>\r\n',
      styles: [".webcam-wrapper{display:inline-block;position:relative;line-height:0}.webcam-wrapper video.mirrored{transform:scaleX(-1)}.webcam-wrapper canvas{display:none}.webcam-wrapper .camera-switch{background-color:#0000001a;background-image:url(data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEAAAABACAYAAACqaXHeAAAE9UlEQVR42u2aT2hdRRTGf+cRQqghSqihdBFDkRISK2KDfzDWxHaRQHEhaINKqa1gKQhd6EZLN+IidCH+Q0oWIkVRC21BQxXRitVaSbKoJSGtYGoK2tQ/tU1jY5v0c5F54Xl7b/KSO/PyEt+3e5f75p7zzZwzZ74zUEIJJfyfYaEGllQGVAGZlENdBy6Z2cSiYFTSKkkfS/pH/nBF0kFJdUW9AiRVASeAukD8DgNrzOySrwEzng18KaDzALXuG8W3AiStAvqBisBRNg40mtlPxbYCOgvgPO4bncWW+JpVeDQXRQhIygDfA00F5r0XuNfMrgclQFI98DDQCNQA5ZFXqoCWBVp8XwHRHeEqcN7loy/NbHBesyqpQ1KfFj/6nC+ZvFaApFrgPaCZpYVvgCfNbDiRAElNwGFg+RIt/X8H2s2s9wYCJDUAR4HqJX7++RN40MwGpgmQVAH0AQ2BPz4AHHPl8nBOAqtyFWQjsA6oL4Ada81sPDv7uwImod8kvSJp9RyS8O2SXnb/DYVd2Y9VSroQ4ANXJO2WVJmixqh0kzMWwL4LkiqRtDnA4D1zmfE8j9g9AezcnAHaPcfXdbfdnPZ2Yps6+DwAvO/Z1naTdApY7Xng48BDZnY1MpMVQBuw3iXc5Tnb0wBwBPjUzP6eoezuArZ6svM0geJLkvZEYnl3nkntoqROSbckSW2Suj3ZOIangc7GPJuUtNGdFIfmMeavktoSSKiW9LMPw30Q8JqkekmjCbOZRhuclLQjgYSNxUBAj6RyZ9ATgUJpUtJTCSR8vpAEXHAyWK5BXYFIGHOlepSAloUk4NEYgyoknQhEwhFJ0e8h6VSaQeerCb5uZgdi9utxYBNwOUD93hIVXswM4INCi6K9wAszFC2DwLOBDjHbYp59karIUnRdzYy/3ClqVklaUhfwTICj7K25OqA7a4wWagVsm4Me/xzwg2cCqqONFzO7DPxSCAJi436GUBgHHguQD2oTlJ55oSzP9ybccsttSJw1szdjFOSnI/8dTCGZHwcORp4Nx7y3B1iZ8/sm4MW8/Euxg5wIsS/HaAp3zeP4/G7obRDXI4jiTIA22H7Xdc7X+S3A5lC7QBQ357aq3VAjCeSkwUfAJrfvz+R8A9ADLAtZB+TinpjC5JMA+//jwPZZnF8G7J+L8z4IWB/zbG+gIujVWfLBW/NStVMmqaG4POJRsIjix7h8IGnLQuoBbQki5sVAJHyYm7YkNaRRtXwQ8G1cHpX0iKRrgUjYno17Sf0LrQhJUkdCeHWkVITGJI0k1QeS3ikGSUzOyJUJJNznYneuOCnpTldcxa2kP3xJYqOeSDjqZG8ShJLnE8TTuMS6Iyu1BW7djZqkfo9N0QOuYJmYQddfB7RG+gLTNzqAY9FrL+5/nwEbvDdJJe3zzOrhNP3AWRqmk55t3ZcBuj3b2gb0Sbrbo/NNzk7fFzu7s/E5EiC+rrmeQU0Kx2skvRFoOx2ZzlmSdgbsw49JetvtBpk8nM64d/cGbNtJ0s7cGyJlwHeEv+t3nqnLSgPAUOSGyG3AHUxdzqoJbEcvcL+ZTeTeEapzJKxgaeOcc/7Mf06D7kFrguS0VDAMtGadv+E47DT9tcChJej8ISfpD+abgTe45uOkFi8mnQ+JBVQ+d4VXuOptjavcyot8pq86mfwk8LWZnaOEEkoooYQSSojDv8AhQNeGfe0jAAAAAElFTkSuQmCC);background-repeat:no-repeat;border-radius:5px;position:absolute;right:13px;top:10px;height:48px;width:48px;background-size:80%;cursor:pointer;background-position:center;transition:background-color .2s ease}.webcam-wrapper .camera-switch:hover{background-color:#0000002e}\n"]
    }]
  }], null, {
    width: [{
      type: Input
    }],
    height: [{
      type: Input
    }],
    videoOptions: [{
      type: Input
    }],
    allowCameraSwitch: [{
      type: Input
    }],
    mirrorImage: [{
      type: Input
    }],
    captureImageData: [{
      type: Input
    }],
    imageType: [{
      type: Input
    }],
    imageQuality: [{
      type: Input
    }],
    imageCapture: [{
      type: Output
    }],
    initError: [{
      type: Output
    }],
    imageClick: [{
      type: Output
    }],
    cameraSwitched: [{
      type: Output
    }],
    video: [{
      type: ViewChild,
      args: ["video", {
        static: true
      }]
    }],
    canvas: [{
      type: ViewChild,
      args: ["canvas", {
        static: true
      }]
    }],
    trigger: [{
      type: Input
    }],
    switchCamera: [{
      type: Input
    }]
  });
})();
var COMPONENTS = [WebcamComponent];
var WebcamModule = class {
};
WebcamModule.ɵfac = function WebcamModule_Factory(__ngFactoryType__) {
  return new (__ngFactoryType__ || WebcamModule)();
};
WebcamModule.ɵmod = ɵɵdefineNgModule({
  type: WebcamModule,
  declarations: [WebcamComponent],
  imports: [CommonModule],
  exports: [WebcamComponent]
});
WebcamModule.ɵinj = ɵɵdefineInjector({
  imports: [[CommonModule]]
});
(() => {
  (typeof ngDevMode === "undefined" || ngDevMode) && setClassMetadata(WebcamModule, [{
    type: NgModule,
    args: [{
      imports: [CommonModule],
      declarations: [COMPONENTS],
      exports: [COMPONENTS]
    }]
  }], null, null);
})();
var WebcamInitError = class {
  constructor() {
    this.message = null;
    this.mediaStreamError = null;
  }
};
var WebcamMirrorProperties = class {
};
export {
  WebcamComponent,
  WebcamImage,
  WebcamInitError,
  WebcamMirrorProperties,
  WebcamModule,
  WebcamUtil
};
//# sourceMappingURL=ngx-webcam.js.map
