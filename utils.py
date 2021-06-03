import os


def get_current_files_size(FILES_LOCATION):
    size = 0
    for file in os.listdir(FILES_LOCATION):
        size += os.path.getsize(f"{FILES_LOCATION}{file}")

    return size


def check_dir(path):
    if not os.path.exists(path):
        os.mkdir(path)