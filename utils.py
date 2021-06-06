import os
import json
from config import Config
from werkzeug.utils import secure_filename


def get_current_files_size(FILES_LOCATION):
    size = 0
    for file in os.listdir(FILES_LOCATION):
        size += os.path.getsize(f"{FILES_LOCATION}{file}")

    return size


def check_dir(path):
    if not os.path.exists(path):
        os.mkdir(path)


def decode_path(path_name):
    if "%2F" in path_name:
        path_name = path_name.replace("%2F", "/")

        path_name = path_name.split("/")
        dir = secure_filename(path_name[0])
        file = secure_filename(path_name[1])

        path_name = f"{dir}/{file}"

    return path_name


def get_users():
    with open(f"{Config.CURRENT_DIR}/users/users.json", "r") as accounts:
        users = json.loads(accounts.read())

    return users
