import tensorflow as tf
import numpy as np
import cv2

from common.SharedFolders import SharedFolders


def predict_object_TF(img):

    size = 128
    img = cv2.resize(img, dsize=(size, size), interpolation=cv2.INTER_CUBIC)

    class_names = ['Apfel', 'Aubergine', 'Avocado', 'Birne',
                   'Granatapfel', 'Kaki', 'Kartoffel', 'Kiwi',
                   'Mandarine', 'Orange', 'Pampelmuse', 'Paprika',
                   'Tomate', 'Zitrone', 'Zucchini', 'Zwiebel']

    model_path = f"{SharedFolders.MODELS}/obst_gemuese_TF_100.h5"
    model = tf.keras.models.load_model(model_path)

    # Bereitet ein Bild für das Modell vor.
    prepared_image = tf.keras.preprocessing.image.img_to_array(img)
    prepared_image = np.expand_dims(prepared_image, axis=0)  # Fügt eine Batch-Dimension hinzu
    prepared_image /= 255.0  # Normalisierung

    # Vorhersage
    predictions = model.predict(prepared_image)
    predicted_class_index = np.argmax(predictions)

    return class_names[predicted_class_index]