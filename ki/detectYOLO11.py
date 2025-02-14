# von Sonja Schwabe
# Klasse um Lebensmittel auf einzelnem Bild von der KI - Yolo11, trainiert mit großem Datensatz, erkennen zu lassen
# Rückgabe ist Klassenname
from ultralytics import YOLO
import cv2
import logging
import os
import numpy


#gibt Dateinamen und Endung getrennt zurück (Bsp. "file.jpg" wird zu "file")
def name_extrahieren(name):
    dateiname,datei_endung =os.path.splitext(name)
    return dateiname,datei_endung

#fragt ab, ob Ergebnis der Objekterkennung korrekt
#TODO anbinden an Frontend
def abfrage(obj):
    #print("Ist " + obj + " korrekt? [y/n]")
    #korrekt_bool = None
    #while korrekt_bool is None:
    #    korrekt = input()
    #    if korrekt == "y":
    #        korrekt_bool = True
    #    elif korrekt == "n":
    #        korrekt_bool = False
    #    else:
    #        print("Bitte wiederholen sie die Angabe und schreiben 'y' oder 'n'")
    #return korrekt_bool
    return True

#Ein Bild von der KI erkennen lassen, je nach Klassifikationsergebnis zum Lernen weiterverarbeiten und Klassennamen zurückgebe
def detect(bild, filename):
    logging.info("Sent to AI for detection.")
    #resizing given image to 224x224
    img=cv2.imread(bild)
    img_small=cv2.resize(img,(224,224))

    model = YOLO("KIModelle/trainiert_mit_ganzem_Datensatz/train65/weights/best.pt") #Laden des trainierten Modells
    #TODO ggf conf niedriger setzen
    results = model(img_small, conf=0.75) #Objekterkennung vom YOLO11-Modell durchführen, dabei nur erkannte Obj mit Konfidenz mind 0,75 beachten

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
        #logging.info("Filename is " + filename)
        dateiname,datei_endung = name_extrahieren(filename)
        #logging.info("Dateiename is " + dateiname)
        labelpfad = "datasets/Testdaten/labels/"
        imagespfad = "datasets/Testdaten/images/"
        best_result.save_txt(labelpfad + dateiname + ".txt")
        logging.info("Resultlabel saved.")
        cv2.imwrite(imagespfad + dateiname + datei_endung,img_small)
    #TODO was wenn nicht richtig?

    train=True
    if train:
        #TODO je nachdem wo alles abgelegt wird anpassen
        metrics_old = model.val(data="datasets/FFv3/data.yaml")
        map50_old = metrics_old.box.map50
        model.train(data="datasets/FFv3/data.yaml", device=0, workers = 0, epochs=1, imgsz=224, batch=16)
        #new_model = YOLO("runs/detect/train/weights/best.pt")
        #metrics_new = new_model.val()
        metrics_new=model.val()
        map50_new=metrics_new.box.map50
        logging.info("old map50 is " + str(map50_old) + " and new map50 is " + str(map50_new))

    return obj_name
