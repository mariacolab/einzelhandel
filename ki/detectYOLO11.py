# von Sonja Schwabe
# Klasse um Lebensmittel auf einzelnem Bild von der KI - Yolo11, trainiert mit großem Datensatz, erkennen zu lassen
# Rückgabe ist Klassenname
import logging
import os
import shutil

import torch
from PIL import Image

from ultralytics import YOLO
from common.SharedFolders import SharedFolders
from testYOLO11 import yolotest

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

    if best_result is None:
        logging.info("please make a better picture and ensure the object is clearly visible")
        if not os.path.exists(f"{SharedFolders.TRAININGSSATZ.value}/YoloErgebnisse/"):
            os.makedirs(f"{SharedFolders.TRAININGSSATZ.value}/YoloErgebnisse/")
        results[0].save(f"{SharedFolders.TRAININGSSATZ.value}/YoloErgebnisse/{name}{endung}")
        results[0].save_txt(f"{SharedFolders.TRAININGSSATZ.value}/{name}.txt")
        return "NONE"

    #Aus dem besten Ergebnis die Klassen-ID extrahieren und dieser den passenden Klassennamen zuordnen
    names= model.names
    obj_id = best_result.boxes.cls
    obj_name =names[int(obj_id)]
    if not os.path.exists(f"{SharedFolders.TRAININGSSATZ.value}/YoloErgebnisse/"):
        os.makedirs(f"{SharedFolders.TRAININGSSATZ.value}/YoloErgebnisse/")
    best_result.save(f"{SharedFolders.TRAININGSSATZ.value}/YoloErgebnisse/{name}{endung}")
    best_result.save_txt(f"{SharedFolders.TRAININGSSATZ.value}/{name}.txt")
    return obj_name

def retrain(): #trainiert ein neues Modell, testet ob dieses besser ist und setzt dieses dementsprechend ggf als neues Modell
    # "cpu" for CPU use or "cuda" for GPU
    device = "cuda" if torch.cuda.is_available() else "cpu"
    logging.info(f"device: {device}")
    # Bisheriges Modell laden
    model_path = f"{SharedFolders.KI_MODELLE_GESAMT_BEST_GEWICHT.value}/best.pt"
    model = YOLO(model_path)
    #map50 und Anzahl korrekt klassifizierter Testbilder ermitteln bei bisherigem Modell
    correct_old = yolotest(f"{SharedFolders.KI_MODELLE_GESAMT_BEST_GEWICHT.value}/best.pt")
    metrics_old = model.val(data=f"{SharedFolders.DATASETS_FFv3.value}/data.yaml", project=f"{SharedFolders.KI_MODELLE_TRAIN_GESAMT.value}", name="oldVal")
    map50_old = metrics_old.box.map50

    #Modell neu trainieren
    save_path= f"{SharedFolders.KI_MODELLE_GESAMT_NEW.value}"
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    model.train(data=f"{SharedFolders.DATASETS_FFv3.value}/data.yaml", project=save_path, device=0, workers=0, epochs=200, imgsz=224, batch=64, patience=40, pretrained=True)
    # map50 und Anzahl korrekt klassifizierter Testbilder ermitteln bei neuem Modell
    correct_new = yolotest(f"{SharedFolders.KI_MODELLE_GESAMT_BEST_GEWICHT.value}/best.pt")
    metrics_new = model.val(project=f"{SharedFolders.KI_MODELLE_TRAIN_GESAMT.value}", name="newVal")
    map50_new = metrics_new.box.map50

    logging.info("aktuelle mAP50 ist " + str(map50_old) + " und neue mAP50 ist " + str(map50_new))
    logging.info("aktuelles Model erkennt " + str(correct_old) + " der 105 Testbilder korrekt und das neue Modell " + str(correct_new))

    betterModell=""
    if map50_new>map50_old and ((map50_new-map50_old) > 0,2):
        logging.info("new is better")
        betterModell = "new"
    elif map50_new>map50_old and (correct_new >= correct_old):
        logging.info("new is better")
        betterModell = "new"
    else:
        logging.info("old is better")
        betterModell = "old"

    #wenn neues Modell besser dieses als neues bestes auswählen und Val-Ordner löschen
    if betterModell == "new":
        #um Platz zu sparen ggf bestModel Gewichte einfach löschen - so gehen die Daten aber nicht verloren
        i = 0
        while os.path.exists(f"{SharedFolders.KI_MODELLE_TRAIN_GESAMT.value}/xbestModelxi"):
            i = i+1
        shutil.copytree(f"{SharedFolders.KI_MODELLE_TRAIN_GESAMT.value}/bestModel",f"{SharedFolders.KI_MODELLE_TRAIN_GESAMT.value}/xbestModelxi")
        shutil.rmtree(f"{SharedFolders.KI_MODELLE_TRAIN_GESAMT.value}/bestModel")
        shutil.copytree(f"{SharedFolders.KI_MODELLE_GESAMT_NEW.value}/train",f"{SharedFolders.KI_MODELLE_GESAMT_BEST.value}")
        shutil.rmtree(f"{SharedFolders.KI_MODELLE_GESAMT_NEW.value}/train")
    shutil.rmtree(f"{SharedFolders.KI_MODELLE_TRAIN_GESAMT.value}/newVal")
    shutil.rmtree(f"{SharedFolders.KI_MODELLE_TRAIN_GESAMT.value}/oldal")

    return