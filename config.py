import os
from consts import DBConsts


class Config:
    CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
    APP_DIR_PATH = os.path.join(CURRENT_DIR, "home_drive")
    MIGRATIONS_DIR_PATH = os.path.join(CURRENT_DIR, "migrations")

    MAX_UPLOAD_SIZE = 200000  # max uploaded file size in MB
    MAX_SHARED_FILES_SIZE = 50000000000  # max size of files stored in system in bytes
    FILES_LOCATION = os.path.join(CURRENT_DIR, "storage", "files")
    TMP_LOCATION = os.path.join(CURRENT_DIR, "storage", "tmp")
    PRIVATE_FILES_LOCATION = os.path.join(CURRENT_DIR, "storage", "private")
    APP_PORT = 8080
    APP_HOST = "0.0.0.0"
    DEBUG_MODE = False
    APP_TIMEOUT = 0
    UPLOAD_CHUNK_SIZE = 4096

    DOWNLOAD_PREVIEW_FILES_TYPES = ("png", "jpg", "pdf", "txt")
    VIDEO_TYPES = ("mp4", "avi")

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_MYSQL_DATABASE_URI = "mysql://root:{password}@{address}/{db_name}"
    SQLALCHEMY_SQLITE_DATABASE_URI = f"sqlite:////{CURRENT_DIR}/database/app.db"

    SQLALCHEMY_DATABASE_URI = ""

    DB_MODE = os.environ.get("DB_MODE", default=DBConsts.SQLITE_DB)
