//von Maria Schuster
const protocol = window.location.protocol; // Liefert "http:" oder "https:"
const host = window.location.hostname;

export const environment = {
  production: false,

  // Dynamische API URLs basierend auf dem aktuellen Protokoll und Host
  apiUrls: {
    userManagement: `${protocol}//${host}/user-management/auth`,
    eventingService: {
      publishCorrectedClassification: `${protocol}//${host}/eventing-service/publish/CorrectedClassification`,
      labeledTrainingData: `${protocol}//${host}/eventing-service/LabeledTrainingdata`,
      imageUploaded: `${protocol}//${host}/eventing-service/ImageUploaded`,
      qrcodeScanResult: `${protocol}//${host}/eventing-service/qrcode/scan/result`,
      tensorflow: `${protocol}//${host}/eventing-service/ai/tensorflow`,
      yolo: `${protocol}//${host}/eventing-service/ai/yolo`,
    },
    externalServices: {
      service5008: `${protocol}//${host}:5008`,
      service5015: `${protocol}//${host}:5015`
    },
  }
};
