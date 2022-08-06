import os
import json
from config import Config
from werkzeug.utils import secure_filename


def get_current_files_size(file_location):
    size = 0
    for file in os.listdir(file_location):
        if os.path.isdir(os.path.join(file_location, file)):
            for file_inside_dir in os.listdir(os.path.join(file_location, file)):
                size += os.path.getsize(os.path.join(file_location, file, file_inside_dir))
        else:
            size += os.path.getsize(os.path.join(file_location, file))

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

        path_name = os.path.join(dir, file)

    return path_name
