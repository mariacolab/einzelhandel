# von Sonja Schwabe
# Klasse um Lebensmittel auf einzelnem Bild von der KI - Yolo11, trainiert mit großem Datensatz, erkennen zu lassen
# Rückgabe ist Klassenname
import logging
import os
import tempfile
import torch
import cv2
from ultralytics import YOLO

from common.DriveFolders import DriveFolders
from common.google_drive import google_get_file_stream, google_uploade_file_to_folder, \
    google_upload_file_to_drive

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
# def detect(bild, filename):
def detect(fileid):
    logging.info("Sent to AI for detection.")
    file_stream = google_get_file_stream(folder_id=DriveFolders.KIModelle_trainiert_mit_ganzem_Datensatz.value,
                                         file_name="bestTrain40.pt")
    logging.info("detect file_stream")
    if file_stream:
        # "KIModelle/trainiert_mit_ganzem_Datensatz/bestTrain40.pt"
        # "cpu" for CPU use or "cuda" for GPU
        device = "cpu" #"cuda" if torch.cuda.is_available() else "cpu"
        logging.info(f"device: {device}")
        # Temporäre Datei für YOLO-Modell erstellen
        with tempfile.NamedTemporaryFile(suffix=".pt", delete=False) as temp_model_file:
            temp_model_file.write(file_stream.read())
            temp_model_path = temp_model_file.name
            model = YOLO(temp_model_path).to(device)
            #logging.info(f"model: {model}")
        # TODO ggf conf niedriger setzen
            file_stream_img = google_get_file_stream(folder_id=DriveFolders.UPLOAD.value,
                                                  file_id=fileid)
            with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp_img_file:
                temp_img_file.write(file_stream_img.read())
                temp_img_path = temp_img_file.name
                results = model(temp_img_path,
                            conf=0.75)  # Objekterkennung vom YOLO11-Modell durchführen, dabei nur erkannte Obj mit Konfidenz mind 0,75 beachten
                logging.info(f"result: {results}")
                # Objekt mit höchster Konfidenz auswählen
                best_result = None
                for result in results[0]:
                    if best_result is None:
                        best_result = result
                    elif result.boxes.conf > best_result.boxes.conf:
                        best_result = result
                    else:
                        logging.info("2 or more classes detected and lower confidences ignored")
                # TODO Falls kein Objekt erkannt wurde
                if best_result is None:
                    logging.info("please make a better picture and ensure the object is clearly visible")
                    return "nichts"

                # Aus dem besten Ergebnis die Klassen-ID extrahieren und dieser den passenden Klassennamen zuordnen
                names = model.names
                obj_id = best_result.boxes.cls
                obj_name = names[int(obj_id)]

        # Nachlernen
        korrekt_bool = abfrage(obj_name)
        if korrekt_bool is True:
            # TODO Pfad wo gespeichert
            # korrekt erkannt -> Bild und Label den Trainingsdaten hinzufügen
            logging.info("Filename is " + file_stream.name)
            dateiname = name_extrahieren(file_stream.name)
            logging.info("Filename is " + dateiname)
            with tempfile.TemporaryDirectory() as temp_dir:
                # labelpfad = "Datasets/TestDaten/labels/"
                # imagespfad = "Datasets/TestDaten/images/"
                # google_move_to_another_folder()
                # label
                # google_stream_file_to_new_file(fileid, dateiname + ".txt", DriveFolders.Datasets_TestDaten_labels.value)

                best_result.save_txt(temp_dir + dateiname + ".txt")
                logging.info("Resultlabel saved.")
                google_uploade_file_to_folder(DriveFolders.Datasets_TestDaten_labels.value,
                                              dateiname + ".txt",
                                              temp_dir)
                # TODO resize
                bild2 = cv2.imread(file_stream)
                # .imwrite(temp_dir + dateiname + ".jpg", bild2)
                google_upload_file_to_drive(DriveFolders.Datasets_TestDaten_labels.value, bild2)

                # image
                # google_stream_file_to_new_file(fileid, dateiname + ".jpg", DriveFolders.Datasets_TestDaten_labels.value)

        # TODO was wenn nicht richtig?

        return obj_name
