# von Sonja Schwabe
# Klasse um Lebensmittel auf einzelnem Bild von der KI - Yolo11, trainiert mit großem Datensatz, erkennen zu lassen
# Rückgabe ist Klassenname
from ultralytics import YOLO
import cv2
import logging

def name_extrahieren(name):
    name1 = str(name)
    name1 = name1.strip("{}'")
    name1 = name1.rstrip(".jpg")
    return name1

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
    model = YOLO("KIModelle/trainiert_mit_ganzem_Datensatz/bestTrain40.pt") #Laden des trainierten Modells
    #TODO ggf conf niedriger setzen
    results = model(bild, conf=0.75) #Objekterkennung vom YOLO11-Modell durchführen, dabei nur erkannte Obj mit Konfidenz mind 0,75 beachten

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

    #Aus dem besten Ergebnis die Klassen-ID extrahieren und diese dem passenden Klassennamen zuordnen
    names= model.names
    obj_id = best_result.boxes.cls
    obj_name =names[int(obj_id)]

    #Nachlernen
    korrekt_bool = abfrage(obj_name)
    if korrekt_bool is True:
        # TODO Pfad wo gespeichert
        # korrekt erkannt -> Bild und Label den Trainingsdaten hinzufügen
        dateiname = name_extrahieren(filename)
        labelpfad = "Datasets/TestDaten/labels/"
        imagespfad = "Datasets/TestDaten/images/"
        best_result.save_txt(labelpfad + dateiname + ".txt")
        logging.info("Resultlabel saved.")
        bild2 = cv2.imread(bild)
        cv2.imwrite(imagespfad + dateiname + ".jpg",bild2)
    #TODO was wenn nicht richtig?

    return obj_name
