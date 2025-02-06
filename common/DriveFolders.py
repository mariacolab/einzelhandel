import enum

class DriveFolders(enum.Enum):
    MODELS = "1epkWoGNRCWeHZbrqMW6okGcmhde1yLQy"  # Replace with actual folder ID
    KIModelle = "13HRqvGLxjQtZwxrOoJQR9JvenIWiQheg"
    Datasets = "1w35_EVX5okPYtZGivVCXQJ-2nWbW1RNQ"
    UPLOAD = "1xoA3-4RWkeizafEYUqfovjgD6Q3oSR7q"
    TRAININGSSATZ = "1BV9kt1H9r9qSUcVAcFjSxFWvOxFfDwYm"
    Datasets_FFv1 = "1Tiw3S-Q2qo85x6mfl6cgMHZVv6nwl1fX"
    Datasets_FFv1_test = "1IbNv1CAXiq8YHVsgql-Vv76pZ1-HnFIe"
    Datasets_FFv1_valid = "18Ttcc8aZ9SMk3FnkrqD-Tp1R2F8ZPxAy"
    Datasets_FFv1_test_labels = "1IbNv1CAXiq8YHVsgql-Vv76pZ1-HnFIe"
    Datasets_FFv1_test_images = "1IbNv1CAXiq8YHVsgql-Vv76pZ1-HnFIe"
    Datasets_FFv1_valid_images = "1GcyMb-yKaE8Sor5sYS1Jjx_b8OAQKMlJ"
    KIModelle_trainiert_mit_ganzem_Datensatz = "1pMRcbhDr0DHNDWD-Nf01zhqNCKhAyYgC"
# Example usage
print(f"Folder Name: {DriveFolders.IMAGES.name}, Folder ID: {DriveFolders.IMAGES.value}")
