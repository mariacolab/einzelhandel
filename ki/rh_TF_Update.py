import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import os
import logging

# Setup logging
logging.basicConfig(level=logging.DEBUG)

def update_model_TF():
    logging.info("Beginn Funktion.")
    # Vorhandenes Modell laden
    model_path = './MODELS/obst_gemuese_TF_100.h5'
    model = load_model(model_path)

    logging.info("Modell geladen.")

    # Verzeichnisse mit neuen Bildern
    base_dir = "./DATA/ObstGemuese_Neu/"
    train_dir = os.path.join(base_dir, '1_TRAIN')
    test_dir = os.path.join(base_dir, '2_TEST')

    # Bildgröße und Batchgröße definieren
    img_size = (128, 128)  # Passe dies an die ursprüngliche Modellarchitektur an
    batch_size = 32

    # Datenvorbereitung mit Augmentation
    train_datagen = ImageDataGenerator(
        rescale=1./255,
        rotation_range=30,
        width_shift_range=0.2,
        height_shift_range=0.2,
        shear_range=0.2,
        zoom_range=0.2,
        horizontal_flip=True,
        fill_mode='nearest')

    test_datagen = ImageDataGenerator(rescale=1./255)

    train_generator = train_datagen.flow_from_directory(
        train_dir,
        target_size=img_size,
        batch_size=batch_size,
        class_mode='categorical')

    test_generator = test_datagen.flow_from_directory(
        test_dir,
        target_size=img_size,
        batch_size=batch_size,
        class_mode='categorical')

    # Modell für das Fine-Tuning vorbereiten
    for layer in model.layers:
        layer.trainable = True  # Falls du nur einige Layer trainieren willst, setze trainable=False für andere

    # Modell kompilieren
    model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=0.0001),
                  loss='categorical_crossentropy',
                  metrics=['accuracy'])

    logging.info("Compile durchgeführt.")

    # Modell mit den neuen Daten weitertrainieren
    epochs = 20  # Kann je nach Bedarf angepasst werden
    model.fit(train_generator,
              epochs=epochs,
              steps_per_epoch=32,
              validation_data=test_generator,
              validation_steps=32)

    logging.info(f"Update durchgeführt!")

    # Aktualisiertes Modell speichern
    updated_model_path = './MODELS/obst_gemuese_TF_100.h5'
    model.save(updated_model_path)

    logging.info(f"Modell gespeichert {updated_model_path}.")
