# von Sonja Schwabe
# Klasse um Lebensmittel auf einzelnem Bild von der KI - Yolo11, trainiert mit großem Datensatz, erkennen zu lassen
# Rückgabe ist Klassenname
import logging
import os

from PIL import Image
import torch

from ultralytics import YOLO

from common.DriveFolders import DriveFolders


logging.info(f"torch available: {torch.cuda.is_available()}")

# gibt Dateinamen ohne Endung zurück (Bsp. "file.jpg" wird zu "file")
def pfad_zerlegen(name):
    path,file = os.path.split(name)
    datei_name, datei_endung = os.path.splitext(file)
    return path, datei_name, datei_endung

# Ein Bild von der KI erkennen lassen, je nach Klassifikationsergebnis zum Lernen weiterverarbeiten und Klassennamen zurückgebe
def detect(bild, filename):
    logging.info("Sent to AI for detection.")

    # "cpu" for CPU use or "cuda" for GPU
    device = "cuda" if torch.cuda.is_available() else "cpu"
    logging.info(f"device: {device}")

    model_path = f"{DriveFolders.KI_MODELLE_BESTMODEL_GEWICHTE.value}/best.pt"
    model = YOLO(model_path).to(device)

    if model is None:
        logging.error("Fehler: Modell konnte nicht geladen werden!")
        return "Fehler: Modell nicht geladen."

    #Bild auf die KI-optimierte Größe bringen
    img_small=bild.resize((224,224))
    results = model(img_small, conf=0.5)  # Objekterkennung vom YOLO11-Modell durchführen, dabei nur erkannte Obj mit Konfidenz mind 0,5 beachten

    # Objekt mit höchster Konfidenz auswählen
    best_result = None
    for result in results[0]:
        if best_result is None:
            best_result = result
        elif result.boxes.conf > best_result.boxes.conf:
            best_result = result
        else:
            logging.info("2 or more classes detected and lower confidences ignored")
    #TODO Falls kein Objekt erkannt wurde
    if best_result is None:
        logging.info("please make a better picture and ensure the object is clearly visible")
        return "NONE"

    #Aus dem besten Ergebnis die Klassen-ID extrahieren und dieser den passenden Klassennamen zuordnen
    names= model.names
    obj_id = best_result.boxes.cls
    obj_name =names[int(obj_id)]

    #TODO was wenn nicht richtig?
    return obj_name, best_result

def retrain():
    # "cpu" for CPU use or "cuda" for GPU
    device = "cuda" if torch.cuda.is_available() else "cpu"
    logging.info(f"device: {device}")
    # TODO je nachdem wo alles abgelegt wird anpassen
    model_path = f"{DriveFolders.KI_MODELLE_BESTMODEL_GEWICHTE.value}/best.pt"
    model = YOLO(model_path)
    logging.info(f"TEST1")
    #metrics_old = model.val(data=f"{DriveFolders.DATASETS_FFv3.value}/data.yaml")
    logging.info(f"TEST2")
    #map50_old = metrics_old.box.map50
    save_path= f"{DriveFolders.KI_MODELLE_NEWMODEL.value}"
    logging.info(f"TEST3")
    model.train(data=f"{DriveFolders.DATASETS_FFv3.value}/data.yaml", save_dir=save_path, device=0, workers=0, epochs=1, imgsz=224, batch=32)
    logging.info(f"TEST4")
    # new_model = YOLO("runs/detect/train/weights/best.pt")
    # metrics_new = new_model.val()
    metrics_new = model.val()
    map50_new = metrics_new.box.map50
    logging.info("old map50 is " + str(map50_old) + " and new map50 is " + str(map50_new))