# von Sonja Schwabe
# Klasse um Lebensmittel auf einzelnem Bild von der KI - Yolo11, trainiert mit großem Datensatz, erkennen zu lassen
# Rückgabe ist Klassenname
import logging
import os

import torch
from PIL import Image

from ultralytics import YOLO
from common.SharedFolders import SharedFolders


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

    model_path = f"{SharedFolders.KI_MODELLE_GESAMT_BEST_GEWICHT.value}/best.pt"
    model = YOLO(model_path).to(device)

    if model is None:
        logging.error("Fehler: Modell konnte nicht geladen werden!")
        return "Fehler: Modell nicht geladen."

    # TODO ggf conf niedriger setzen
    img_small = bild.resize((224, 224))
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

    #Bild speichern in Trainingssatz
    pfad,name,endung=pfad_zerlegen(filename)
    img_small.save(f"{SharedFolders.TRAININGSSATZ.value}/{name}{endung}")

    #TODO Falls kein Objekt erkannt wurde
    if best_result is None:
        logging.info("please make a better picture and ensure the object is clearly visible")
        results[0].save(f"{SharedFolders.TRAININGSSATZ.value}/YoloErgebnisse/{name}{endung}")
        results[0].save_txt(f"{SharedFolders.TRAININGSSATZ.value}/{name}.txt")
        return "NONE"

    #Aus dem besten Ergebnis die Klassen-ID extrahieren und dieser den passenden Klassennamen zuordnen
    names= model.names
    obj_id = best_result.boxes.cls
    obj_name =names[int(obj_id)]
    best_result.save(f"{SharedFolders.TRAININGSSATZ.value}/YoloErgebnisse/{name}{endung}")
    best_result.save_txt(f"{SharedFolders.TRAININGSSATZ.value}/{name}.txt")
    return obj_name

def retrain():
    # "cpu" for CPU use or "cuda" for GPU
    device = "cuda" if torch.cuda.is_available() else "cpu"
    logging.info(f"device: {device}")
    # TODO je nachdem wo alles abgelegt wird anpassen
    model_path = f"{SharedFolders.KI_MODELLE_GESAMT_BEST_GEWICHT.value}/best.pt"
    model = YOLO(model_path)
    logging.info(f"TEST1")
    metrics_old = model.val(data=f"{SharedFolders.DATASETS_FFv3.value}/data.yaml")
    logging.info(f"TEST2")
    map50_old = metrics_old.box.map50
    save_path= f"{SharedFolders.KI_MODELLE_GESAMT_NEW.value}"
    logging.info(f"TEST3")
    model.train(data=f"{SharedFolders.DATASETS_FFv3.value}/data.yaml", save_dir=save_path, device=0, workers=0, epochs=1, imgsz=224, batch=32)
    logging.info(f"TEST4")
    metrics_new = model.val()
    map50_new = metrics_new.box.map50
    logging.info("old map50 is " + str(map50_old) + " and new map50 is " + str(map50_new))
    if map50_new>map50_old:
        io