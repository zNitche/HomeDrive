import os


def getCurrentFilesSize(FILES_LOCATION):
    size = 0
    for file in os.listdir(FILES_LOCATION):
        size += os.path.getsize(f"{FILES_LOCATION}{file}")

    return size