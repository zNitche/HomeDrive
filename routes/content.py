from flask import render_template, Blueprint, redirect, url_for, request, send_file
from flask import current_app as app
import flask_login
import os
from Utils import get_current_files_size, check_dir
from Permissions import max_private_files_size


MAX_UPLOAD_SIZE = app.config["MAX_UPLOAD_SIZE"]
FILES_LOCATION = app.config["FILES_LOCATION"]
CURRENT_DIR = app.config["CURRENT_DIR"]
MAX_SHARED_FILES_SIZE = app.config["MAX_SHARED_FILES_SIZE"]
TMP_LOCATION = app.config["TMP_LOCATION"]
PRIVATE_FILES_LOCATION = app.config["PRIVATE_FILES_LOCATION"]
app.config['MAX_CONTENT_LENGTH'] = MAX_UPLOAD_SIZE * 1024 * 1024


content_ = Blueprint("content", __name__, template_folder='template', static_folder='static')


@content_.route("/")
def home():
    if flask_login.current_user.is_authenticated:
        files = os.listdir(FILES_LOCATION)

        current_size = f"{str(round(get_current_files_size(FILES_LOCATION) / 1000000000, 2))} GB"
        max_size = f"{MAX_SHARED_FILES_SIZE / 1000000000} GB"

        can_delete = flask_login.current_user.can_delete_files
        can_upload = flask_login.current_user.can_upload
        have_private_space = flask_login.current_user.have_private_space

        return render_template("index.html", files=files, max_size=max_size, current_size=current_size,
                               can_delete=can_delete, can_upload=can_upload, have_private_space=have_private_space)
    else:
        return redirect(url_for("auth.login"))


@content_.route("/private")
@flask_login.login_required
def private():
    if flask_login.current_user.have_private_space:
        user = flask_login.current_user.id
        check_dir(f"{PRIVATE_FILES_LOCATION}{user}")

        files = os.listdir(f"{PRIVATE_FILES_LOCATION}{user}")

        current_size = f"{str(round(get_current_files_size(f'{PRIVATE_FILES_LOCATION}{user}/') / 1000000000, 2))} GB"
        max_size = f"{max_private_files_size(user) / 1000000000} GB"

        can_delete = flask_login.current_user.can_delete_files
        can_upload = flask_login.current_user.can_upload
        have_private_space = flask_login.current_user.have_private_space

        return render_template("private.html", files=files, max_size=max_size, current_size=current_size,
                                have_private_space=have_private_space)
    else:
        return redirect(url_for("content.home"))


@content_.route("/upload")
@flask_login.login_required
def upload_view():
    can_upload = flask_login.current_user.can_upload

    files = os.listdir(FILES_LOCATION)

    current_size = f"{str(round(get_current_files_size(FILES_LOCATION) / 1000000000, 2))} GB"
    max_size = f"{MAX_SHARED_FILES_SIZE / 1000000000} GB"

    have_private_space = flask_login.current_user.have_private_space

    return render_template("upload.html", files=files, max_size=max_size, current_size=current_size,
                               have_private_space=have_private_space, can_upload=can_upload)


@content_.route("/main/upload", methods=["POST"])
@flask_login.login_required
def upload():
    file = request.files["file-upload"]

    if file.filename == "":
        return redirect(url_for("content.home"))

    space = request.form["space"]

    if space == "shared":
        if file.filename in os.listdir(FILES_LOCATION):
            files = os.listdir(FILES_LOCATION)

            current_size = f"{str(round(get_current_files_size(FILES_LOCATION) / 1000000000, 2))} GB"
            max_size = f"{MAX_SHARED_FILES_SIZE / 1000000000} GB"

            can_delete = flask_login.current_user.can_delete_files
            can_upload = flask_login.current_user.can_upload
            have_private_space = flask_login.current_user.have_private_space

            return render_template("index.html", files=files, max_size=max_size, current_size=current_size,
                                   can_delete=can_delete, can_upload=can_upload, have_private_space=have_private_space)

        if flask_login.current_user.can_upload:
            file.save(f"{TMP_LOCATION}shared/{file.filename}")

            if (os.path.getsize(f"{TMP_LOCATION}shared/{file.filename}")) + get_current_files_size(FILES_LOCATION) < MAX_SHARED_FILES_SIZE:
                os.rename(f"{TMP_LOCATION}shared/{file.filename}", f"{FILES_LOCATION}{file.filename}")
            else:
                os.remove(f"{TMP_LOCATION}shared/{file.filename}")

        return redirect(url_for("content.home"))

    elif space == "private" and flask_login.current_user.have_private_space:
        user = flask_login.current_user.id

        check_dir(f"{PRIVATE_FILES_LOCATION}{user}")

        if file.filename in os.listdir(f"{PRIVATE_FILES_LOCATION}{user}"):
            files = os.listdir(f"{PRIVATE_FILES_LOCATION}{flask_login.current_user.id}")

            current_size = f"{str(round(get_current_files_size(f'{PRIVATE_FILES_LOCATION}{user}/') / 1000000000, 2))} GB"
            max_size = f"{max_private_files_size(user) / 1000000000} GB"

            can_delete = flask_login.current_user.can_delete_files
            can_upload = flask_login.current_user.can_upload
            have_private_space = flask_login.current_user.have_private_space

            return render_template("private.html", files=files, max_size=max_size, current_size=current_size,
                                   have_private_space=have_private_space)

        check_dir(f"{TMP_LOCATION}{user}")

        file.save(f"{TMP_LOCATION}{user}/{file.filename}")

        if (os.path.getsize(f"{TMP_LOCATION}{user}/{file.filename}")) + get_current_files_size(
                f'{PRIVATE_FILES_LOCATION}{user}/') < MAX_SHARED_FILES_SIZE:

            os.rename(f"{TMP_LOCATION}{user}/{file.filename}", f"{PRIVATE_FILES_LOCATION}{user}/{file.filename}")
        else:
            os.remove(f"{TMP_LOCATION}{user}/{file.filename}")

        return redirect(url_for("content.private"))

    else:
        return redirect(url_for("content.home"))


@content_.route("/main/operations", methods=["GET", "POST"])
@flask_login.login_required
def operations():
    if request.args.get("download_file"):
        file_name = request.args.get("download_file")
        return redirect(url_for("content.download", file_name=file_name))
    elif request.args.get("delete_file"):
        file_name = request.args.get("delete_file")
        return redirect(url_for("content.delete", file_name=file_name))


@content_.route("/main/operations_private", methods=["GET", "POST"])
@flask_login.login_required
def operations_private():
    if flask_login.current_user.have_private_space:
        if request.args.get("download_file"):
            file_name = request.args.get("download_file")
            return redirect(url_for("content.download_private", file_name=file_name))
        elif request.args.get("delete_file"):
            file_name = request.args.get("delete_file")
            return redirect(url_for("content.delete_private", file_name=file_name))


@content_.route("/main/download_private/<file_name>", methods=["GET"])
@flask_login.login_required
def download_private(file_name):
    if flask_login.current_user.have_private_space:
        if file_name.endswith(".pdf") or file_name.endswith(".jpg") or file_name.endswith(".png"):
            return send_file(f"{PRIVATE_FILES_LOCATION}{flask_login.current_user.id}/{file_name}",
                             as_attachment=False, attachment_filename=f'{file_name}', cache_timeout=0)
        else:
            return send_file(f"{PRIVATE_FILES_LOCATION}{flask_login.current_user.id}/{file_name}",
                             as_attachment=True, attachment_filename=f'{file_name}', cache_timeout=0)


@content_.route("/main/delete_private/<file_name>", methods=["GET"])
@flask_login.login_required
def delete_private(file_name):
    if flask_login.current_user.have_private_space:
        os.remove(f"{PRIVATE_FILES_LOCATION}{flask_login.current_user.id}/{file_name}")

    return redirect(url_for("content.private"))


@content_.route("/main/download/<file_name>", methods=["GET"])
@flask_login.login_required
def download(file_name):
    if file_name.endswith(".pdf") or file_name.endswith(".jpg") or file_name.endswith(".png"):
        return send_file(f'{FILES_LOCATION}{file_name}', as_attachment=False, attachment_filename=f'{file_name}', cache_timeout=0)
    else:
        return send_file(f'{FILES_LOCATION}{file_name}', as_attachment=True, attachment_filename=f'{file_name}', cache_timeout=0)


@content_.route("/main/delete/<file_name>", methods=["GET"])
@flask_login.login_required
def delete(file_name):
    if flask_login.current_user.can_delete_files:
        os.remove(f"{FILES_LOCATION}{file_name}")

    return redirect(url_for("content.home"))


@app.errorhandler(404)
def not_found(error):
    return render_template("error.html", message=error)


@app.errorhandler(500)
def overloaded(error):
    return render_template("error.html", message=error)


@app.errorhandler(401)
def non_authenticated(error):
    return redirect(url_for("auth.login"))


@app.errorhandler(405)
def method_not_allowed(error):
    return render_template("error.html", message=error)