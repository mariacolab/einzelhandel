# Ralf Hager
# Matr.Nr.: 3924238
# Diese Funktion trainiert ein CNN auf das Erkennen von Bildern von 16 Klassen
# Obst oder Gemüse.
#
# Es wird außerhalb des Systems einzelhandel lokal ausgeführt, um ein Initiales Modell zur Verfügung 
# zu stellen.
#
# Neben der eigentlichen Modell- und Trainingsaufrufe wird insbesondere die Ausgabe der Modellparameter,
# der unterschiedlichen Metriken und der Confusion Matrix ausgeführt.
#
import warnings
import numpy as np
import matplotlib.pyplot as plt
import os
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Activation, Dropout, BatchNormalization
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.metrics import Precision, Recall, AUC
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import seaborn as sns

from sklearn.utils.class_weight import compute_class_weight
from sklearn.metrics import classification_report, confusion_matrix

# Visualisierung der Trainingsmetriken
def plot_training(history):
    plt.figure(figsize=(12, 5))

    plt.subplot(1, 2, 1)
    plt.plot(history.history['loss'], label='Train Loss')
    plt.plot(history.history['val_loss'], label='Val Loss')
    plt.legend()
    plt.title('Loss Verlauf')

    plt.subplot(1, 2, 2)
    plt.plot(history.history['accuracy'], label='Train Acc')
    plt.plot(history.history['val_accuracy'], label='Val Acc')
    plt.legend()
    plt.title('Accuracy Verlauf')
    plt.show()

def train_TF_Modell(epochs):
    # Beispiel: 16 Klassen (Anpassung notwendig, falls weniger oder mehr Klassen vorhanden sind
    n_classes = 16
    input_shape = (128, 128, 3)
    basis = "./DATA/ObstGemuese/"
    os.environ["KMP_DUPLICATE_LIB_OK"]="TRUE"

    # Modell definieren
    model = Sequential()

    model.add(Conv2D(filters=32, kernel_size=(3, 3), input_shape=input_shape, activation='relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))

    model.add(Conv2D(filters=64, kernel_size=(3, 3), activation='relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))

    model.add(Conv2D(filters=128, kernel_size=(3, 3), activation='relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))

    model.add(Flatten())
    model.add(Dense(256, activation='relu'))
    model.add(Dropout(0.5))
    model.add(Dense(128, activation='relu'))

    model.add(Dense(n_classes, activation='softmax'))

    # Modell kompilieren
    model.compile(loss='categorical_crossentropy',
                  optimizer=Adam(learning_rate=0.001),
                  metrics=['accuracy', Precision(name='precision'), Recall(name='recall'), AUC(name='auc')])

    # Modellübersicht
    model.summary()

    batch_size = 32
    image_shape = (128, 128, 3)  # Falls nicht definiert, stelle sicher, dass es korrekt ist

    # Trainingsdaten vorbereiten
    train_image_gen = ImageDataGenerator(
        rotation_range=30,
        width_shift_range=0.1,
        height_shift_range=0.1,
        rescale=1 / 255,
        shear_range=0.2,
        zoom_range=0.2,
        horizontal_flip=True,
        fill_mode='nearest'
    )

    train_image_gen = train_image_gen.flow_from_directory(
        basis + '1_TRAIN/',
        target_size=image_shape[:2],
        batch_size=batch_size,
        class_mode='categorical'
    )

    valid_image_gen = ImageDataGenerator(rescale=1.0 / 255)
    valid_image_gen = valid_image_gen.flow_from_directory(
        basis + '3_VALIDATE/',
        target_size=image_shape[:2],
        batch_size=batch_size,
        class_mode='categorical'
    )

    # Labels extrahieren
    class_indices = train_image_gen.class_indices  # Dictionary {Klassenname: Index}
    y_train = train_image_gen.classes  # Array mit numerischen Klassenlabels
    y_train_one_hot = np.eye(len(class_indices))[y_train]  # One-Hot-Codierung

    # Training und Validierung des Modells
    warnings.filterwarnings('ignore')
    results = model.fit(
        train_image_gen,
        epochs=epochs,
        steps_per_epoch=len(train_image_gen),
        validation_data=valid_image_gen,
        validation_steps=len(valid_image_gen)
    )

    # Ausgabe der Trainingsergebnisse des Modells
    plot_training(results)

    # Speichern des Modells
    model.save('./MODEL/obst_gemuese_TF_' + str(epochs) + '_final.h5')


    # Modelltestdaten vorbereiten
    test_image_gen = ImageDataGenerator(rescale=1.0 / 255)
    test_image_gen = test_image_gen.flow_from_directory(
        basis + '2_TEST/',
        target_size=image_shape[:2],
        batch_size=batch_size,
        class_mode='categorical',
        shuffle=False
    )

    # Modell testen mittels der Testdaten
    test_image_gen.reset()
    y_test = test_image_gen.classes
    y_test_one_hot = to_categorical(y_test, num_classes=len(class_indices))

    # Modellbewertung
    y_pred = model.predict(test_image_gen, steps=len(test_image_gen), verbose=1)
    y_pred_classes = np.argmax(y_pred, axis=1)

    # Classification Report ausgeben
    print("Classification Report:")
    print(classification_report(y_test, y_pred_classes))

    # Konfusionsmatrix visualisieren
    cm = confusion_matrix(y_test, y_pred_classes)
    plt.figure(figsize=(6, 5))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=range(n_classes), yticklabels=range(n_classes))
    plt.xlabel("Vorhergesagte Klasse")
    plt.ylabel("Tatsächliche Klasse")
    plt.title("Konfusionsmatrix")
    plt.show()

#
# Hauptfunktion: Hier wird die Anzahl der Epochen an die Trainingsfunktion mitgegeben 
#
if __name__=="__main__":
    
    epochs = 15
    
    train_TF_Modell(epochs)

