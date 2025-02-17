import enum

class DriveFolders(enum.Enum):
    BASE = "/mnt/gdrive"

    # Hauptordner
    MODELS = f"{BASE}/MODELS"
    KI_MODELLE = f"{BASE}/KIModelle"
    DATASETS = f"{BASE}/Datasets"
    UPLOAD = f"{BASE}/UPLOAD"
    TRAININGSSATZ = f"{BASE}/TRAININGSSATZ"
    DATA = f"{BASE}/DATA"

    # Datasets-Unterordner
    DATASETS_FFv1 = f"{DATASETS}/FFv1"
    DATASETS_FFv1_TEST = f"{DATASETS_FFv1}/test"
    DATASETS_FFv1_VALID = f"{DATASETS_FFv1}/valid"
    DATASETS_FFv1_TEST_LABELS = f"{DATASETS_FFv1_TEST}/labels"
    DATASETS_FFv1_TEST_IMAGES = f"{DATASETS_FFv1_TEST}/images"
    DATASETS_FFv1_VALID_IMAGES = f"{DATASETS_FFv1_VALID}/images"
    DATASETS_FFv3 = f"{DATASETS}/FFv3"
    DATASETS_FFv3_TRAIN = f"{DATASETS_FFv3}/train"
    DATASETS_FFv3_TEST = f"{DATASETS_FFv3}/test"
    DATASETS_FFv3_VALID = f"{DATASETS_FFv3}/valid"
    DATASETS_FFv3_TRAIN_LABELS = f"{DATASETS_FFv3_TRAIN}/labels"
    DATASETS_FFv3_TRAIN_IMAGES = f"{DATASETS_FFv3_TRAIN}/images"
    DATASETS_FFv3_TEST_LABELS = f"{DATASETS_FFv3_TEST}/labels"
    DATASETS_FFv3_TEST_IMAGES = f"{DATASETS_FFv3_TEST}/images"
    DATASETS_FFv3_VALID_LABELS = f"{DATASETS_FFv3_VALID}/labels"
    DATASETS_FFv3_VALID_IMAGES = f"{DATASETS_FFv3_VALID}/images"

    DATASETS_TESTDATEN = f"{DATASETS}/TestDaten"
    DATASETS_TESTDATEN_LABELS = f"{DATASETS_TESTDATEN}/labels"
    DATASETS_TESTDATEN_IMAGES = f"{DATASETS_TESTDATEN}/images"

    # KI Modelle
    KI_MODELLE_TRAIN_GESAMT = f"{KI_MODELLE}/trainiert_mit_ganzem_Datensatz"
    KI_MODELLE_BESTMODEL = f"{KI_MODELLE_TRAIN_GESAMT}/bestModel"
    KI_MODELLE_NEWMODEL = f"{KI_MODELLE_TRAIN_GESAMT}/newModel"
    KI_MODELLE_BESTMODEL_GEWICHTE = f"{KI_MODELLE_BESTMODEL}/weights"

    # Obst und Gemüse Datensätze
    DATA_OBST_GEMUESE = f"{DATA}/ObstGemuese"
    DATA_OBST_GEMUESE_NEU_1_TRAIN = f"{DATA_OBST_GEMUESE}/Neu_1/TRAIN"
    DATA_OBST_GEMUESE_NEU_2_TEST = f"{DATA_OBST_GEMUESE}/Neu_2/TEST"
    DATA_OBST_GEMUESE_NEU_3_VALIDATE = f"{DATA_OBST_GEMUESE}/Neu_3/VALIDATE"

    # Obst und Gemüse Trainingsdaten
    DATA_OBST_GEMUESE_NEU_1_TRAIN_TOMATE = f"{DATA_OBST_GEMUESE_NEU_1_TRAIN}/Tomate"
    DATA_OBST_GEMUESE_NEU_1_TRAIN_PAPRIKA = f"{DATA_OBST_GEMUESE_NEU_1_TRAIN}/Paprika"
    DATA_OBST_GEMUESE_NEU_1_TRAIN_ORANGE = f"{DATA_OBST_GEMUESE_NEU_1_TRAIN}/Orange"
    DATA_OBST_GEMUESE_NEU_1_TRAIN_KAKI = f"{DATA_OBST_GEMUESE_NEU_1_TRAIN}/Kaki"
    DATA_OBST_GEMUESE_NEU_1_TRAIN_AUBERGINE = f"{DATA_OBST_GEMUESE_NEU_1_TRAIN}/Aubergine"
    DATA_OBST_GEMUESE_NEU_1_TRAIN_APFEL = f"{DATA_OBST_GEMUESE_NEU_1_TRAIN}/Apfel"

    # Obst und Gemüse Testdaten
    DATA_OBST_GEMUESE_NEU_2_TEST_TOMATE = f"{DATA_OBST_GEMUESE_NEU_2_TEST}/Tomate"
    DATA_OBST_GEMUESE_NEU_2_TEST_PAPRIKA = f"{DATA_OBST_GEMUESE_NEU_2_TEST}/Paprika"
    DATA_OBST_GEMUESE_NEU_2_TEST_ORANGE = f"{DATA_OBST_GEMUESE_NEU_2_TEST}/Orange"
    DATA_OBST_GEMUESE_NEU_2_TEST_KAKI = f"{DATA_OBST_GEMUESE_NEU_2_TEST}/Kaki"
    DATA_OBST_GEMUESE_NEU_2_TEST_AUBERGINE = f"{DATA_OBST_GEMUESE_NEU_2_TEST}/Aubergine"
    DATA_OBST_GEMUESE_NEU_2_TEST_APFEL = f"{DATA_OBST_GEMUESE_NEU_2_TEST}/Apfel"

    # Obst und Gemüse Validierungsdaten
    DATA_OBST_GEMUESE_NEU_3_VALIDATE_TOMATE = f"{DATA_OBST_GEMUESE_NEU_3_VALIDATE}/Tomate"
    DATA_OBST_GEMUESE_NEU_3_VALIDATE_PAPRIKA = f"{DATA_OBST_GEMUESE_NEU_3_VALIDATE}/Paprika"
    DATA_OBST_GEMUESE_NEU_3_VALIDATE_ORANGE = f"{DATA_OBST_GEMUESE_NEU_3_VALIDATE}/Orange"
    DATA_OBST_GEMUESE_NEU_3_VALIDATE_KAKI = f"{DATA_OBST_GEMUESE_NEU_3_VALIDATE}/Kaki"
    DATA_OBST_GEMUESE_NEU_3_VALIDATE_AUBERGINE = f"{DATA_OBST_GEMUESE_NEU_3_VALIDATE}/Aubergine"
    DATA_OBST_GEMUESE_NEU_3_VALIDATE_APFEL = f"{DATA_OBST_GEMUESE_NEU_3_VALIDATE}/Apfel"
