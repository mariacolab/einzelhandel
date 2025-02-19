#von Sonja Schwabe
#Klasse, die alle Bilder aus dem Test Ordner durch das KI-Modell testen lässt und prüft, ob diese Richtig erkannt wurden

from ultralytics import YOLO
import os
import logging

from common.SharedFolders import SharedFolders


#TODO Modell übergeben
def yolotest(modelpath):
    #Pfade setzen
    path_img = f"{SharedFolders.DATASETS_FFv3_TEST_IMAGES.value}"
    path_labels = f"{SharedFolders.DATASETS_FFv3_TEST_LABELS.value}"
    model = YOLO(modelpath)  # Laden des trainierten Modells
    results = model(path_img, conf=0.01, stream=False) #alle Bilder des Testordners erkennen lassen

    #Listen für spätere Berechnungen anlegen und initialsieren
    anzahl = list(range(47))
    correct = list(range(47))
    for i in range (0,47):
        anzahl[i] = 0
        correct[i] = 0

    for result in results:
        #zugehöriges Label-Dokument öffnen
        pfad, datei = os.path.split(result.path)
        dateiname, endung = os.path.splitext(datei)
        label = open(path_labels + '/' + dateiname + ".txt", 'r')
        zeile = label.readline()
        zeile_zerteilt = zeile.split(" ",1)
        anzahl[int(zeile_zerteilt[0])] += 1 #den Zähler für die in dem Bild zu erkennende Klasse in der Anzahl-Liste erhöhen

        #bei mehreren Ergebnissen nur das mit höchster Konfidenz beachten (im Testordner gibt es nur Bilder, zu denen genau eine Sache erkannt werden soll)
        boxes = result.boxes
        best_result = None
        for box in boxes:
            if best_result is None:
                best_result = box
            elif box.conf > best_result.conf:
                best_result = box
        if best_result is None: #nichts erkannt -> Fehler, diesen Schleifendurchgang abbrechen
            continue
        #prüfen, ob gefundene Klasse mit gelabelter Klasse übereinstimmt
        class_id = int(best_result.cls)
        if zeile.startswith(str(class_id)):
            correct[int(zeile_zerteilt[0])] +=1 #falls korrekt, Zähler in der Korrekt-Liste an der Stelle der Klassen-ID erhöhren
        label.close()

    #TODO
    #Ausgeben der Ergebnisse
    class_names = model.names
    for i in range (0,46):
        print(class_names[i] +": von " +str(anzahl[i])+ " Bildern sind " + str(correct[i]) + " korrekt zugeordnet. In Prozent: " + str((correct[i]/anzahl[i])*100))
        anzahl[46] += anzahl[i]
        correct[46] += correct[i]
    print ('Gesamtergebnis: ' + str(correct[46]) + ' von ' +str(anzahl[46])+ ' sind korrekt. In Prozent: ' + str((correct[46]/anzahl[46])*100))
    return int(correct[46])

