# Ralf Hager
# Matr.Nr. 3924238
#
# Modul: rh_TF_Update
# 
# Beschreibung: 
# 
# In diesem Modul wird das Nachtraining eines vortrainierten Modells durchgeführt.
# Hierzu müssen die Daten für das Nachtraining im Ordner 1_Training, sowie 
# 2_Test zur Verfügung gestellt werden.
# 
# Alternativ hierzu können die Daten auch in die Trainingsdaten des Gesamtmodells aufgenommen werden 
# und dann mit der Funktion train_TF_Modell() das Gesamttraining durchgeführt werden.
#
#
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import os
import logging
from PIL import Image

from common.SharedFolders import SharedFolders

# Setup logging
logging.basicConfig(level=logging.DEBUG)

#
# Function:     move_Data_TF
#
# Parameter:    path
#               labels
#               file_names
#
# Beschreibung:
#
# Die im path enthaltenen Files werden gelesen,
# auf das Format 128x128 umformatiert
# und ins Verzeichnis Trainings-Verzeichnis geschrieben.
# Dies dient als Vorbereitung des Nachlern-Schrittes
#

def move_Data_TF(path, labels, file_names):
    logging.info("move_Data_TF")
    base_dir = f'{SharedFolders.DATA_OBST_GEMUESE.value}'
    train_dir = os.path.join(base_dir, '1_TRAIN')

    os.makedirs(train_dir, exist_ok=True)

    for file_name, label in zip(file_names, labels):
        logging.info(f"move_Data_TF {file_name}, {label}")
        label_dir = os.path.join(train_dir, label)
        os.makedirs(label_dir, exist_ok=True)

        file_path = os.path.join(path, file_name)
        if not os.path.exists(file_path):
            logging.error(f"move_data_TF: Datei existiert nicht: {file_path}")
            continue
        try:
            image = Image.open(file_path)
            target_path = os.path.join(label_dir, file_name)
            img_small = image.resize((128, 128))
            img_small.save(f"{target_path}")
        except Exception as e:
            logging.error(f"Error in move_Data_TF: {e}")

#
# Function: delete_files_in_directory
#
# Parameter:    train_dir
#
# Beschreibung:
#
# Die im train_dir enthaltenen Files aus dem train_dir gelöscht.
# Damit ist sichergestellt, dass einmal gelernte Daten nicht mehrfach
# nachgelernt werden.
#

def delete_files_in_directory(train_dir):
    if not os.path.exists(train_dir):
        logging.error(f"delete_files_in_directory: Verzeichnis existiert nicht: {train_dir}")
        return
    for root, dirs, files in os.walk(train_dir):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                os.remove(file_path)
                logging.info(f"Gelöscht: {file_path}")
            except Exception as e:
                logging.error(f"Fehler beim Löschen von {file_path}: {e}")
#
# Function: update_model_TF
# Parameter:
#
# Beschreibung:
#
# Die Funktion führt das Nach-Training eines bereits vortrainierten Modells durch.
# Die dazu notwendigen Daten sind in den Ordnern 1_Train und 2_Test bereitzustellen
#
# Das bestehende Modell wird am ende der Funktion durch das aktualisierte Modell überschrieben.
# Die Anzahl der für das Nachtraining durchzuführenden Epochen kann in der Funktion gesetzt werden.
#
def update_model_TF():
    # Vorhandenes Modell laden
    model_path = f'{SharedFolders.MODELS.value}/obst_gemuese_TF_250.h5'
    model = load_model(model_path)

    logging.info("Modell geladen.")

    # Verzeichnisse mit neuen Bildern
    base_dir = f'{SharedFolders.DATA_OBST_GEMUESE.value}'
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
    # Kann bei Bedarf angepasst werden

    epochs = 50
    model.fit(train_generator,
              epochs=epochs,
              steps_per_epoch=32,
              validation_data=test_generator,
              validation_steps=32)

    logging.info(f"Update durchgeführt!")

    # Aktualisiertes Modell speichern
    updated_model_path = f'{SharedFolders.MODELS.value}/obst_gemuese_TF_250.h5'
    model.save(updated_model_path)

    # Nach dem Nachlernen werden die Daten aus dem Trainingsverzeichnis gelöscht.
    delete_files_in_directory(train_dir)

    logging.info(f"Modell gespeichert {updated_model_path}.")