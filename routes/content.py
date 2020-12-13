from flask import render_template, Blueprint, redirect, url_for, request, send_file
from flask import current_app as app
import flask_login
import os
from Utils import getCurrentFilesSize


MAX_UPLOAD_SIZE = app.config["MAX_UPLOAD_SIZE"]
FILES_LOCATION = app.config["FILES_LOCATION"]
CURRENT_DIR = app.config["CURRENT_DIR"]
MAX_FILES_SIZE = app.config["MAX_FILES_SIZE"]
TMP_LOCATION = app.config["TMP_LOCATION"]
app.config['MAX_CONTENT_LENGTH'] = MAX_UPLOAD_SIZE * 1024 * 1024


content_ = Blueprint("content", __name__, template_folder='template', static_folder='static')


@content_.route("/")
def home():
    if flask_login.current_user.is_authenticated:
        files = os.listdir(FILES_LOCATION)

        current_size = f"{str(round(getCurrentFilesSize(FILES_LOCATION) / 1000000000, 2))} GB"
        max_size = f"{MAX_FILES_SIZE/1000000000} GB"
        return render_template("index.html", files=files, max_size=max_size, current_size=current_size)
    else:
        return redirect(url_for("auth.login"))


@content_.route("/main/upload", methods=["POST"])
@flask_login.login_required
def upload():
    file = request.files["file-upload"]

    if file.filename == "":
        return redirect(url_for("content.home"))

    if file.filename in os.listdir(FILES_LOCATION):
        message = "File already exists"
        files = os.listdir(FILES_LOCATION)

        current_size = f"{str(round(getCurrentFilesSize(FILES_LOCATION) / 1000000000, 2))} GB"
        max_size = f"{MAX_FILES_SIZE / 1000000000} GB"

        return render_template("index.html", message=message, files=files, max_size=max_size, current_size=current_size)

    file.save(f"{TMP_LOCATION}{file.filename}")

    if (os.path.getsize(f"{TMP_LOCATION}{file.filename}")) + getCurrentFilesSize(FILES_LOCATION) < MAX_FILES_SIZE:
        os.rename(f"{TMP_LOCATION}{file.filename}", f"{FILES_LOCATION}{file.filename}")
    else:
        os.remove(f"{TMP_LOCATION}{file.filename}")

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


@content_.route("/main/download/<file_name>", methods=["GET"])
@flask_login.login_required
def download(file_name):
    return send_file(f'{FILES_LOCATION}{file_name}', as_attachment=True, attachment_filename=f'{file_name}', cache_timeout=0)


@content_.route("/main/delete/<file_name>", methods=["GET"])
@flask_login.login_required
def delete(file_name):
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