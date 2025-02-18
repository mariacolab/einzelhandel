# von Sonja Schwabe
# Klasse um Lebensmittel auf einzelnem Bild von der KI - Yolo11, trainiert mit großem Datensatz, erkennen zu lassen
# Rückgabe ist Klassenname
import logging
import os

import cv2
import torch

from ultralytics import YOLO
from common.SharedFolders import SharedFolders


logging.info(f"torch available: {torch.cuda.is_available()}")


# gibt Dateinamen ohne Endung zurück (Bsp. "file.jpg" wird zu "file")
def name_extrahieren(name):
    dateiname, datei_endung = os.path.splitext(name)
    return dateiname


# fragt ab, ob Ergebnis der Objekterkennung korrekt
# TODO anbinden an Frontend
def abfrage(obj):
    # print("Ist " + obj + " korrekt? [y/n]")
    # korrekt_bool = None
    # while korrekt_bool is None:
    #    korrekt = input()
    #    if korrekt == "y":
    #        korrekt_bool = True
    #    elif korrekt == "n":
    #        korrekt_bool = False
    #    else:
    #        print("Bitte wiederholen sie die Angabe und schreiben 'y' oder 'n'")
    # return korrekt_bool
    return True


# Ein Bild von der KI erkennen lassen, je nach Klassifikationsergebnis zum Lernen weiterverarbeiten und Klassennamen zurückgebe
def detect(bild, filename):
    logging.info("Sent to AI for detection.")

    # "cpu" for CPU use or "cuda" for GPU
    device = "cuda" if torch.cuda.is_available() else "cpu"
    logging.info(f"device: {device}")

    model_path = f"{SharedFolders.KI_MODELLE_TRAIN_GESAMT.value}/bestTrain40.pt"
    model = YOLO(model_path).to(device)

    if model is None:
        logging.error("Fehler: Modell konnte nicht geladen werden!")
        return "Fehler: Modell nicht geladen."

    # TODO ggf conf niedriger setzen
    results = model(bild, conf=0.75)  # Objekterkennung vom YOLO11-Modell durchführen, dabei nur erkannte Obj mit Konfidenz mind 0,75 beachten
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
        return "nichts"

    #Aus dem besten Ergebnis die Klassen-ID extrahieren und dieser den passenden Klassennamen zuordnen
    names= model.names
    obj_id = best_result.boxes.cls
    obj_name =names[int(obj_id)]

    #Nachlernen
    korrekt_bool = abfrage(obj_name)
    if korrekt_bool is True:
        # TODO Pfad wo gespeichert
        # korrekt erkannt -> Bild und Label den Trainingsdaten hinzufügen
        logging.info("Filename is " + filename)
        dateiname = name_extrahieren(filename)
        logging.info("Filename is " + dateiname)
        best_result.save_txt(SharedFolders.DATASETS_TESTDATEN_LABELS.value + dateiname + ".txt")
        logging.info("Resultlabel saved.")
        #TODO resize [@Sonja Der Part hat bei mir noch nicht funktioniert, deswegen hab ich es für testzwecke auskommentiert, der zweite rückgabe wert fehlt noch]
        #bild2 = cv2.imread(bild)
        #cv2.imwrite(SharedFolders.DATASETS_TESTDATEN_IMAGES.value + dateiname + ".jpg",bild2)
    #TODO was wenn nicht richtig?

    return obj_name, ""