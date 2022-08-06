from flask import render_template, Blueprint, redirect, url_for, request
from flask import current_app as app
import flask_login
import os
from home_drive import utils


FILES_LOCATION = app.config["FILES_LOCATION"]
MAX_SHARED_FILES_SIZE = app.config["MAX_SHARED_FILES_SIZE"]
PRIVATE_FILES_LOCATION = app.config["PRIVATE_FILES_LOCATION"]
VIDEO_TYPES = app.config["VIDEO_TYPES"]


content_ = Blueprint("content", __name__, template_folder='template', static_folder='static')


@content_.route("/")
def home():
    if flask_login.current_user.is_authenticated:
        files = os.listdir(FILES_LOCATION)

        current_size = f"{str(round(utils.get_current_files_size(FILES_LOCATION) / 1000000000, 2))} GB"
        max_size = f"{MAX_SHARED_FILES_SIZE / 1000000000} GB"

        user_name = flask_login.current_user.id

        can_delete = permissions.can_delete(user_name)
        can_upload = permissions.can_upload(user_name)
        have_private_space = permissions.have_private_space(user_name)

        return render_template("index.html", files=files, max_size=max_size, current_size=current_size,
                               can_delete=can_delete, can_upload=can_upload, have_private_space=have_private_space,
                               video_types=VIDEO_TYPES)

    else:
        return redirect(url_for("auth.login"))


@content_.route("/private")
@flask_login.login_required
def private():
    if flask_login.current_user.have_private_space:
        files = []
        dirs = []

        user_name = flask_login.current_user.id
        utils.check_dir(os.path.join(PRIVATE_FILES_LOCATION, user_name))

        objects_path = os.path.join(PRIVATE_FILES_LOCATION, user_name)
        objects = os.listdir(objects_path)

        for obj in objects:
            if os.path.isdir(os.path.join(objects_path, obj)):
                dirs.append(obj)

            else:
                files.append(obj)

        max_private_size = permissions.max_private_files_size(user_name)

        current_size = f"{str(round(utils.get_current_files_size(os.path.join(PRIVATE_FILES_LOCATION, user_name)) / 1000000000, 2))} GB"
        max_size = f"{max_private_size / 1000000000} GB"

        return render_template("private.html", files=files, dirs=dirs, max_size=max_size, current_size=current_size,
                               video_types=VIDEO_TYPES)

    else:
        return redirect(url_for("content.home"))


@content_.route("/upload")
@flask_login.login_required
def upload_view():
    user_name = flask_login.current_user.id

    if permissions.have_private_space(user_name) or permissions.can_upload(user_name):
        have_private_space = permissions.have_private_space(user_name)
        can_upload = permissions.can_upload(user_name)

        current_size = f"{str(round(utils.get_current_files_size(FILES_LOCATION) / 1000000000, 2))} GB"
        max_size = f"{MAX_SHARED_FILES_SIZE / 1000000000} GB"

        return render_template("upload.html", max_size=max_size, current_size=current_size,
                                   have_private_space=have_private_space, can_upload=can_upload)
    else:
        return redirect(url_for("content.home"))


@content_.route("/private/create_dir")
@flask_login.login_required
def new_directory_view():
    user_name = flask_login.current_user.id

    if permissions.have_private_space(user_name):
        have_private_space = permissions.have_private_space(user_name)
        can_upload = permissions.can_upload(user_name)

        current_size = f"{str(round(utils.get_current_files_size(FILES_LOCATION) / 1000000000, 2))} GB"
        max_size = f"{MAX_SHARED_FILES_SIZE / 1000000000} GB"

        return render_template("directory.html", max_size=max_size, current_size=current_size,
                               have_private_space=have_private_space, can_upload=can_upload)
    else:
        return redirect(url_for("content.home"))


@content_.route("/private/<dir_name>")
@flask_login.login_required
def directory_content(dir_name):
    user_name = flask_login.current_user.id

    if permissions.have_private_space(user_name):
        objects_path = os.path.join(PRIVATE_FILES_LOCATION, user_name)

        if os.path.exists(os.path.join(objects_path, dir_name)):
            files = os.listdir(os.path.join(objects_path, dir_name))

            max_private_size = permissions.max_private_files_size(user_name)

            current_size = f"{str(round(utils.get_current_files_size(os.path.join(PRIVATE_FILES_LOCATION, user_name)) / 1000000000, 2))} GB"
            max_size = f"{max_private_size / 1000000000} GB"

            return render_template("directory_content.html", files=files, max_size=max_size, current_size=current_size,
                                   dir_name=dir_name)
        else:
            return redirect(url_for("content.private"))
    else:
        return redirect(url_for("content.home"))


@content_.route("/content/move/<file_name>", methods=["GET", "POST"])
@flask_login.login_required
def move_file(file_name):
    user_name = flask_login.current_user.id

    if permissions.have_private_space(user_name):
        objects_path = os.path.join(PRIVATE_FILES_LOCATION, user_name)

        dirs = ["/"]
        objects = os.listdir(objects_path)

        for obj in objects:
            if os.path.isdir(os.path.join(objects_path, obj)):
                dirs.append(obj)

        return render_template("move_file.html", dirs=dirs, file_name=file_name)
    else:
        return redirect(url_for("content.home"))


@content_.route("/content/operations", methods=["GET", "POST"])
@flask_login.login_required
def operations():
    if request.args.get("download_file"):
        return redirect(url_for("files_operations.download", file_name=request.args.get("download_file")))

    elif request.args.get("delete_file"):
        return redirect(url_for("files_operations.delete", file_name=request.args.get("delete_file")))

    elif request.args.get("watch_video"):
        return redirect(url_for("files_operations.watch", file_name=request.args.get("watch_video")))


@content_.route("/content/operations_private", methods=["GET", "POST"])
@flask_login.login_required
def operations_private():
    user_name = flask_login.current_user.id
    have_private_space = permissions.have_private_space(user_name)

    if have_private_space:
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
