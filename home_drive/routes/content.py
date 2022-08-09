from flask import render_template, Blueprint, redirect, url_for, request, flash
from flask import current_app as app
import flask_login
import os
from home_drive import utils
from home_drive.decorators import private_space_required


FILES_LOCATION = app.config["FILES_LOCATION"]
MAX_SHARED_FILES_SIZE = app.config["MAX_SHARED_FILES_SIZE"]
PRIVATE_FILES_LOCATION = app.config["PRIVATE_FILES_LOCATION"]
VIDEO_TYPES = app.config["VIDEO_TYPES"]


content = Blueprint("content", __name__, template_folder='template', static_folder='static')


@content.route("/")
def home():
    if flask_login.current_user.is_authenticated:
        files = os.listdir(FILES_LOCATION)

        current_size = f"{str(round(utils.get_current_files_size(FILES_LOCATION) / 1000000000, 2))} GB"
        max_size = f"{MAX_SHARED_FILES_SIZE / 1000000000} GB"

        return render_template("index.html", files=files, max_size=max_size, current_size=current_size,
                               video_types=VIDEO_TYPES)

    else:
        return redirect(url_for("auth.login"))


@content.route("/private")
@flask_login.login_required
@private_space_required
def private():
    files = []
    dirs = []

    user_name = flask_login.current_user.username
    utils.check_dir(os.path.join(PRIVATE_FILES_LOCATION, user_name))

    objects_path = os.path.join(PRIVATE_FILES_LOCATION, user_name)
    objects = os.listdir(objects_path)

    for obj in objects:
        if os.path.isdir(os.path.join(objects_path, obj)):
            dirs.append(obj)

        else:
            files.append(obj)

    max_private_size = flask_login.current_user.max_files_size

    current_size = f"{str(round(utils.get_current_files_size(os.path.join(PRIVATE_FILES_LOCATION, user_name)) / 1000000000, 2))} GB"
    max_size = f"{max_private_size / 1000000000} GB"

    return render_template("private.html", files=files, dirs=dirs, max_size=max_size, current_size=current_size,
                           video_types=VIDEO_TYPES)


@content.route("/upload")
@flask_login.login_required
def upload_view():
    current_user = flask_login.current_user

    if current_user.have_private_space or current_user.can_upload:
        current_size = f"{str(round(utils.get_current_files_size(FILES_LOCATION) / 1000000000, 2))} GB"
        max_size = f"{MAX_SHARED_FILES_SIZE / 1000000000} GB"

        return render_template("upload.html", max_size=max_size, current_size=current_size)

    else:
        return redirect(url_for("content.home"))


@content.route("/private/create_dir")
@flask_login.login_required
@private_space_required
def new_directory_view():
    current_size = f"{str(round(utils.get_current_files_size(FILES_LOCATION) / 1000000000, 2))} GB"
    max_size = f"{MAX_SHARED_FILES_SIZE / 1000000000} GB"

    return render_template("directory.html", max_size=max_size, current_size=current_size)


@content.route("/private/<dir_name>")
@flask_login.login_required
@private_space_required
def directory_content(dir_name):
    current_user = flask_login.current_user

    objects_path = os.path.join(PRIVATE_FILES_LOCATION, current_user.username)

    if os.path.exists(os.path.join(objects_path, dir_name)):
        files = os.listdir(os.path.join(objects_path, dir_name))

        max_private_size = current_user.max_files_size

        current_size = f"{str(round(utils.get_current_files_size(os.path.join(PRIVATE_FILES_LOCATION, current_user.username)) / 1000000000, 2))} GB"
        max_size = f"{max_private_size / 1000000000} GB"

        return render_template("directory_content.html", files=files, max_size=max_size, current_size=current_size,
                               dir_name=dir_name)

    else:
        return redirect(url_for("content.private"))


@content.route("/content/move/<file_name>", methods=["GET", "POST"])
@flask_login.login_required
@private_space_required
def move_file(file_name):
    current_user = flask_login.current_user

    objects_path = os.path.join(PRIVATE_FILES_LOCATION, current_user.username)

    dirs = ["/"]
    objects = os.listdir(objects_path)

    for obj in objects:
        if os.path.isdir(os.path.join(objects_path, obj)):
            dirs.append(obj)

    return render_template("move_file.html", dirs=dirs, file_name=file_name)


@content.route("/content/operations", methods=["GET", "POST"])
@flask_login.login_required
def operations():
    if request.args.get("download_file"):
        return redirect(url_for("files_operations.download", file_name=request.args.get("download_file")))

    elif request.args.get("delete_file"):
        return redirect(url_for("files_operations.delete", file_name=request.args.get("delete_file")))

    elif request.args.get("watch_video"):
        return redirect(url_for("files_operations.watch", file_name=request.args.get("watch_video")))


@content.route("/content/operations_private", methods=["GET", "POST"])
@flask_login.login_required
@private_space_required
def operations_private():
    if request.args.get("download_file"):
        return redirect(url_for("files_operations.download_private", file_name=request.args.get("download_file")))

    elif request.args.get("delete_file"):
        return redirect(url_for("files_operations.delete_private", file_name=request.args.get("delete_file")))

    elif request.args.get("browse_dir"):
        return redirect(url_for("content.directory_content", dir_name=request.args.get("browse_dir")))

    elif request.args.get("move_file"):
        return redirect(url_for("content.move_file", file_name=request.args.get("move_file")))

    elif request.args.get("watch_video"):
        return redirect(url_for("files_operations.watch_private", file_name=request.args.get("watch_video")))
