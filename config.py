import os


class Config:
    CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
    APP_DIR_PATH = os.path.join(CURRENT_DIR, "home_drive")
    MIGRATIONS_DIR_PATH = os.path.join(CURRENT_DIR, "migrations")

    MAX_UPLOAD_SIZE = 200000  # max uploaded file size in MB
    MAX_SHARED_FILES_SIZE = 50000000000  # max size of files stored in system in bytes
    FILES_LOCATION = os.path.join(APP_DIR_PATH, "storage", "files")
    TMP_LOCATION = os.path.join(APP_DIR_PATH, "storage", "tmp")
    PRIVATE_FILES_LOCATION = os.path.join(APP_DIR_PATH, "storage", "private")
    APP_PORT = 8080
    APP_HOST = "0.0.0.0"
    DEBUG_MODE = False
    APP_TIMEOUT = 0
    UPLOAD_CHUNK_SIZE = 4096

    DOWNLOAD_PREVIEW_FILES_TYPES = ("png", "jpg", "pdf", "txt")
    VIDEO_TYPES = ("mp4", "avi")

    SQLALCHEMY_DATABASE_URI = "mysql://root:{password}@{address}/{db_name}".format(
        password=os.environ.get("MYSQL_ROOT_PASSWORD"),
        address=os.environ.get("MYSQL_SERVER_HOST"),
        db_name=os.environ.get("DB_NAME")
    )
