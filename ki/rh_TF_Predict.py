import tempfile

import tensorflow as tf
import numpy as np
import cv2
import logging
from PIL import Image
from common.google_drive import google_get_file_stream
from common.DriveFolders import DriveFolders


logging.basicConfig(level=logging.DEBUG)

def predict_object_TF(fileid):
    # Model aus Google Drive als Stream abrufen
    model_stream = google_get_file_stream(folder_id=DriveFolders.MODELS.value, file_name="obst_gemuese_TF_50.h5")

    if model_stream is None:
        logging.error("Error: Model file stream is empty!")
        return None, "Fehler: Modell nicht gefunden."


    with tempfile.NamedTemporaryFile(suffix=".h5", delete=False) as temp_model_file:
        temp_model_file.write(model_stream.read())  # Speichert den Stream als Datei
        temp_model_path = temp_model_file.name

    logging.info(f"Modell erfolgreich gespeichert: {temp_model_path}")
    model = tf.keras.models.load_model(temp_model_path, compile=False)  # Falls das Modell nicht geladen werden konnte

    # Bild aus Google Drive als Stream abrufen
    file_stream_img = google_get_file_stream(folder_id=DriveFolders.UPLOAD.value, file_id=fileid)

    if file_stream_img is None:
        logging.error("Error: File stream is empty!")
        return "Fehler: Datei nicht gefunden oder leer."

    logging.info("File stream erfolgreich abgerufen.")

    try:
        file_stream_img.seek(0)  # Stelle sicher, dass der Stream am Anfang ist
        image = Image.open(file_stream_img)
        image = image.convert("RGB")  # In RGB umwandeln
    except Exception as e:
        logging.error(f"Fehler beim Öffnen des Bildes: {str(e)}")
        return "Fehler: Ungültiges Bildformat."

    # Bild in NumPy Array umwandeln
    img = np.array(image)
    size = 128
    img = cv2.resize(img, dsize=(size, size), interpolation=cv2.INTER_CUBIC)

    prepared_image = tf.keras.preprocessing.image.img_to_array(img)
    prepared_image = np.expand_dims(prepared_image, axis=0)  # Batch-Dimension hinzufügen
    prepared_image /= 255.0  # Normalisierung

    predictions = model.predict(prepared_image)
    predicted_class_index = np.argmax(predictions)

    class_names = ['Apfel', 'Aubergine', 'Avocado', 'Birne',
                   'Granatapfel', 'Kaki', 'Kartoffel', 'Kiwi',
                   'Mandarine', 'Orange', 'Pampelmuse', 'Paprika',
                   'Tomate', 'Zitrone', 'Zucchini', 'Zwiebel']

    return class_names[predicted_class_index]






