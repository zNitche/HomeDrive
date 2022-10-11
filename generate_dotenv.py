import os
import argparse
from consts import DBConsts


def get_mysql_config():
    args = {
        "DB_MODE": DBConsts.MYSQL_DB,
        "MYSQL_ROOT_PASSWORD": "test_pass",
        "MYSQL_SERVER_PORT": "3306",
        "MYSQL_SERVER_HOST": "db",
        "DB_NAME": "app_db",
        "DB_PATH": "./database/mysql",
        "STORAGE_FILES_PATH": "",
        "STORAGE_PRIVATE_PATH": "",
        "STORAGE_TMP_PATH": ""
    }

    return args


def get_sqlite_config():
    args = {
        "DB_MODE": DBConsts.SQLITE_DB,
        "DB_PATH": "./database",
        "STORAGE_FILES_PATH": "",
        "STORAGE_PRIVATE_PATH": "",
        "STORAGE_TMP_PATH": ""
    }

    return args


def generate(path, config):
    parsed_args = [f"{key}={config[key]}" for key in config]

    with open(path, "a") as file:
        for line in parsed_args:
            file.write(line)
            file.write("\n")


def get_config_for_db_mode(mode):
    config = {}

    if mode == DBConsts.MYSQL_DB:
        config = get_mysql_config()

    elif mode == DBConsts.SQLITE_DB:
        config = get_sqlite_config()

    return config


def main(args):
    db_mode = args.db_mode

    current_dir = os.path.dirname(os.path.realpath(__file__))
    env_path = os.path.join(current_dir, ".env")

    if os.path.exists(env_path):
        print("Removing existing .env file...")

        os.remove(env_path)

    print("Generating .env config file...")

    generate(env_path, get_config_for_db_mode(db_mode))

    print("Generated .env config file...")


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--db_mode", type=str, default=DBConsts.MYSQL_DB,
                        help=f"Database type",
                        choices=[DBConsts.SQLITE_DB, DBConsts.MYSQL_DB])

    return parser.parse_args()


if __name__ == '__main__':
    main(get_args())

