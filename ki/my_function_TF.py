import logging

import tensorflow as tf
import numpy as np
from common.DriveFolders import DriveFolders
from common.google_drive import google_get_file_stream
import matplotlib.pyplot as plt


def predict_object_TF(fileid):
    logging.info("predict_object_TF")
    file_stream = google_get_file_stream(folder_id=DriveFolders.UPLOAD.value,
                                          file_id=fileid)
    logging.info("file_stream")
    #img_file = f"{event_path}{event_filename}"
    img = plt.imread(file_stream)  # Lädt das Bild als NumPy-Array
    img = np.resize(img, (128, 128, 3))
    class_names = ['Apfel', 'Aubergine', 'Avocado', 'Birne',
                   'Granatapfel', 'Kaki', 'Kartoffel', 'Kiwi',
                   'Mandarine', 'Orange', 'Pampelmuse', 'Paprika',
                   'Tomate', 'Zitrone', 'Zucchini', 'Zwiebel']
    file_stream2 = google_get_file_stream(DriveFolders.MODELS, "obst_gemuese_TF_50.h5")

    if file_stream:
        #model_path = "./MODELS/obst_gemuese_TF_50.h5"
        model = tf.keras.models.load_model(file_stream2)


        # Bereitet ein Bild für das Modell vor.
        prepared_image = tf.keras.preprocessing.image.img_to_array(img)
        prepared_image = np.expand_dims(prepared_image, axis=0)  # Fügt eine Batch-Dimension hinzu
        prepared_image /= 255.0  # Normalisierung

        # Vorhersage
        predictions = model.predict(prepared_image)
        predicted_class_index = np.argmax(predictions)

        return class_names[predicted_class_index]

