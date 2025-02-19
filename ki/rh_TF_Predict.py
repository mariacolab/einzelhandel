import tensorflow as tf
import numpy as np

from common.SharedFolders import SharedFolders


def predict_object_TF(img):

    size = 128
    img_small = img.resize((size, size))

    class_names = ['Apfel', 'Aubergine', 'Avocado', 'Birne',
                   'Granatapfel', 'Kaki', 'Kartoffel', 'Kiwi',
                   'Mandarine', 'Orange', 'Pampelmuse', 'Paprika',
                   'Tomate', 'Zitrone', 'Zucchini', 'Zwiebel']

    model_path = f"{SharedFolders.MODELS.value}/obst_gemuese_TF_250.h5"
    model = tf.keras.models.load_model(model_path)

    # Bereitet ein Bild für das Modell vor.
    prepared_image = tf.keras.preprocessing.image.img_to_array(img_small)
    prepared_image = np.expand_dims(prepared_image, axis=0)  # Fügt eine Batch-Dimension hinzu
    prepared_image /= 255.0  # Normalisierung

    # Vorhersage
    predictions = model.predict(prepared_image)
    predicted_class_index = np.argmax(predictions)

    return class_names[predicted_class_index]