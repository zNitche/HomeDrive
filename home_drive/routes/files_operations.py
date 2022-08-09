from flask import render_template, Blueprint, redirect, url_for, request, send_file, make_response, jsonify, flash
import flask_login
from flask import current_app as app
import shutil
import os
from werkzeug.utils import secure_filename
from home_drive import utils
from home_drive.decorators import private_space_required


files_operations = Blueprint("files_operations", __name__, template_folder='template', static_folder='static')


FILES_LOCATION = app.config["FILES_LOCATION"]
MAX_SHARED_FILES_SIZE = app.config["MAX_SHARED_FILES_SIZE"]
TMP_LOCATION = app.config["TMP_LOCATION"]
PRIVATE_FILES_LOCATION = app.config["PRIVATE_FILES_LOCATION"]
UPLOAD_CHUNK_SIZE = app.config["UPLOAD_CHUNK_SIZE"]
DOWNLOAD_PREVIEW_FILES_TYPES = app.config["DOWNLOAD_PREVIEW_FILES_TYPES"]


@files_operations.route("/files_operations/download_private/<file_name>", methods=["GET"])
@flask_login.login_required
@private_space_required
def download_private(file_name):
    current_user = flask_login.current_user

    file_name = utils.decode_path(file_name)
    as_attachment = True

    file_extension = file_name.split(".")[-1].lower()

    if file_extension.endswith(DOWNLOAD_PREVIEW_FILES_TYPES):
        as_attachment = False

    return send_file(os.path.join(PRIVATE_FILES_LOCATION, current_user.username, file_name),
                     as_attachment=as_attachment, download_name=file_name, max_age=0)


@files_operations.route("/files_operations/watch_private/<file_name>", methods=["GET"])
@flask_login.login_required
@private_space_required
def watch_private(file_name):
    file_name = utils.decode_path(file_name)

    return send_file(os.path.join(PRIVATE_FILES_LOCATION, flask_login.current_user.id, file_name),
                     as_attachment=False, download_name=file_name, max_age=0)


@files_operations.route("/files_operations/delete_private/<file_name>", methods=["GET"])
@flask_login.login_required
@private_space_required
def delete_private(file_name):
    current_user = flask_login.current_user

    private_root = os.path.join(PRIVATE_FILES_LOCATION, current_user.username)

    file_name = utils.decode_path(file_name)

    if os.path.isdir(os.path.join(private_root, file_name)):
        shutil.rmtree(os.path.join(private_root, file_name))

    else:
        os.remove(os.path.join(private_root, file_name))

    return redirect(url_for("content.private"))


@files_operations.route("/files_operations/download/<file_name>", methods=["GET"])
@flask_login.login_required
def download(file_name):
    as_attachment = True

    file_extension = file_name.split(".")[-1].lower()

    if file_extension.endswith(DOWNLOAD_PREVIEW_FILES_TYPES):
        as_attachment = False

    return send_file(os.path.join(FILES_LOCATION, file_name), as_attachment=as_attachment,
                     download_name=file_name,
                     max_age=0)


@files_operations.route("/files_operations/delete/<file_name>", methods=["GET"])
@flask_login.login_required
def delete(file_name):
    current_user = flask_login.current_user

    if current_user.can_delete_files:
        os.remove(os.path.join(FILES_LOCATION, file_name))

    return redirect(url_for("content.home"))


@files_operations.route("/files_operations/watch/<file_name>", methods=["GET"])
@flask_login.login_required
def watch(file_name):
    file_name = utils.decode_path(file_name)

    return send_file(os.path.join(FILES_LOCATION, file_name), as_attachment=False, download_name=file_name,
                     max_age=0)


@files_operations.route("/files_operations/create_dir/process", methods=["POST"])
@flask_login.login_required
@private_space_required
def create_new_directory():
    current_user = flask_login.current_user

    dir_name = request.form["dir_name"]
    dir_name = secure_filename(dir_name)

    if dir_name:
        path_to_user_files = os.path.join(PRIVATE_FILES_LOCATION, current_user.username)

        if dir_name in os.listdir(path_to_user_files):
            flash("Directory exists", "error")

            return redirect(url_for("content.directory_content"))

        else:
            os.mkdir(os.path.join(path_to_user_files, dir_name))

            flash(f"Created directory {dir_name}", "success")

            return redirect(url_for("content.private"))

    else:
        flash("Directory name can't be empty", "error")

        return redirect(url_for("content.directory_content"))


@files_operations.route("/files_operations/upload/finalize/move", methods=["POST", "GET"])
@flask_login.login_required
def move_upload():
    current_user = flask_login.current_user
    can_upload = current_user.can_upload
    have_private_space = current_user.have_private_space

    if can_upload or have_private_space:
        tmp_file_path = os.path.join(TMP_LOCATION, current_user.username, "tmp_file")

        if os.path.exists(tmp_file_path):
            file_name = secure_filename(request.form["file_name"])
            dir_name = secure_filename(request.form["dirs"])
            space = request.form["space"]

            if can_upload and space == "shared":
                if os.path.getsize(tmp_file_path) + utils.get_current_files_size(
                        FILES_LOCATION) < MAX_SHARED_FILES_SIZE:

                    if not os.path.exists(os.path.join(FILES_LOCATION, file_name)):
                        shutil.copy2(tmp_file_path, os.path.join(FILES_LOCATION, file_name))

                        os.remove(tmp_file_path)

                        return redirect(url_for("content.home"))

                    else:
                        flash("File already exists, choose different name", "error")

                        return redirect(url_for("files_operations.finalize_upload"))

                else:
                    os.remove(tmp_file_path)

                    return redirect(url_for("content.home"))

            if have_private_space and space == "private":
                if os.path.getsize(tmp_file_path) + utils.get_current_files_size(
                        FILES_LOCATION) < MAX_SHARED_FILES_SIZE:

                    files_root_path = os.path.join(PRIVATE_FILES_LOCATION, current_user.username)

                    if dir_name == "/":
                        dest_path = os.path.join(files_root_path, file_name)

                    else:
                        dest_path = os.path.join(files_root_path, dir_name, file_name)

                    if not os.path.exists(dest_path):
                        shutil.copy2(tmp_file_path, dest_path)

                        os.remove(tmp_file_path)

                        return redirect(url_for("content.private"))
                    else:
                        flash("File already exists, choose different name", "error")

                        return redirect(url_for("files_operations.finalize_upload"))

                else:
                    os.remove(tmp_file_path)

                    return redirect(url_for("content.home"))


@files_operations.route("/files_operations/upload/finalize", defaults={"file_name": ""}, methods=["GET"])
@files_operations.route("/files_operations/upload/finalize/<file_name>", methods=["GET"])
@flask_login.login_required
def finalize_upload(file_name):
    current_user = flask_login.current_user
    can_upload = current_user.can_upload
    have_private_space = current_user.have_private_space

    if can_upload or have_private_space:
        objects_root = os.path.join(PRIVATE_FILES_LOCATION, current_user.username)
        objects = os.listdir(objects_root)
        dirs = ["/"]

        for obj in objects:
            if os.path.isdir(os.path.join(objects_root, obj)):
                dirs.append(obj)

        if os.path.exists(os.path.join(TMP_LOCATION, current_user.username, "tmp_file")):
            return render_template("finalize.html", dirs=dirs, file_name=file_name)

        else:
            return redirect(url_for("content.home"))

    else:
        return redirect(url_for("content.home"))


@files_operations.route("/files_operations/upload", methods=["POST"])
@flask_login.login_required
def upload():
    current_user = flask_login.current_user
    can_upload = current_user.can_upload
    have_private_space = current_user.have_private_space

    if can_upload or have_private_space:
        utils.check_dir(os.path.join(TMP_LOCATION, current_user.username))

        tmp_file_path = os.path.join(TMP_LOCATION, current_user.username, "tmp_file")

        # Getting filename from POST request header
        # filename = request.headers["X-File-Name"]

        if os.path.exists(tmp_file_path):
            os.remove(tmp_file_path)

        with open(tmp_file_path, "wb") as data:
            while True:
                file_chunk = request.stream.read(UPLOAD_CHUNK_SIZE)

                if len(file_chunk) <= 0:
                    break

                data.write(file_chunk)

        return make_response(jsonify(message="OK"), 200)

    else:
        return make_response(jsonify(message="authorization error"), 401)


@files_operations.route("/files_operations/move/process", methods=["POST"])
@flask_login.login_required
def move_file_process():
    # TODO rework this one
    current_user = flask_login.current_user

    if current_user.have_private_space:
        objects_path = os.path.join(PRIVATE_FILES_LOCATION, current_user.username)

        dirs = ["/"]
        objects = os.listdir(objects_path)

        for obj in objects:
            if os.path.isdir(os.path.join(objects_path, obj)):
                dirs.append(obj)

        if request.form["dirs"]:
            objects_root = os.path.join(PRIVATE_FILES_LOCATION, current_user.username)

            dest_dir = request.form["dirs"]
            file_name = request.form["file_name"]
            file_name = utils.decode_path(file_name)

            decoded_name_splited = file_name.split("/")

            if not dest_dir == "/":
                dest_dir = secure_filename(dest_dir)

            else:
                dest_dir = objects_root

            if len(decoded_name_splited) < 2:
                file_name = file_name.split("/")[0]

                file_name = secure_filename(file_name)

                file_path = os.path.join(objects_root, file_name)

            else:
                file_dir = file_name.split("/")[0]
                file_name = file_name.split("/")[1]

                file_name = secure_filename(file_name)
                file_dir = secure_filename(file_dir)

                file_path = os.path.join(objects_root, file_dir, file_name)

            dest_path = os.path.join(objects_root, dest_dir, file_name)

            shutil.move(file_path, dest_path)

            return redirect(url_for("content.private"))

        else:
            flash("Choose directory first", "error")

            return redirect(url_for("content.move_file"))

    else:
        return redirect(url_for("content.home"))
