import os


class Config:
    CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
    MAX_UPLOAD_SIZE = 2000  # max uploaded file size in MB
    MAX_FILES_SIZE = 50000000000 # max size of files stored in system in bytes
    FILES_LOCATION = f"{CURRENT_DIR}/files/"
    TMP_LOCATION = f"{CURRENT_DIR}/tmp/"
    APP_PORT = 8080