import os
from config import Config
import multiprocessing


def setup_sqlite_db():
    db_uri = Config.SQLALCHEMY_SQLITE_DATABASE_URI
    db_config = {
        "pool_recycle": 10,
        "pool_pre_ping": True
    }

    return db_uri, db_config


def setup_mysql_db():
    db_uri = Config.SQLALCHEMY_MYSQL_DATABASE_URI.format(
        password=os.environ.get("MYSQL_ROOT_PASSWORD"),
        address=os.environ.get("MYSQL_SERVER_HOST"),
        db_name=os.environ.get("DB_NAME"))

    db_config = {
        "pool_size": multiprocessing.cpu_count() - 1 + 10,
        "pool_recycle": 10,
        "pool_pre_ping": True
    }

    return db_uri, db_config
