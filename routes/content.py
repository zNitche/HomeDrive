from flask import render_template, Blueprint, redirect, url_for, request, send_file
from flask import current_app as app
import flask_login
import os
from utils import get_current_files_size, check_dir
import permissions
import shutil
from werkzeug.utils import secure_filename


MAX_UPLOAD_SIZE = app.config["MAX_UPLOAD_SIZE"]
FILES_LOCATION = app.config["FILES_LOCATION"]
CURRENT_DIR = app.config["CURRENT_DIR"]
MAX_SHARED_FILES_SIZE = app.config["MAX_SHARED_FILES_SIZE"]
TMP_LOCATION = app.config["TMP_LOCATION"]
PRIVATE_FILES_LOCATION = app.config["PRIVATE_FILES_LOCATION"]
LEGACY_UPLOAD = app.config["LEGACY_UPLOAD"]
UPLOAD_CHUNK_SIZE = app.config["UPLOAD_CHUNK_SIZE"]
app.config['MAX_CONTENT_LENGTH'] = MAX_UPLOAD_SIZE * 1024 * 1024


content_ = Blueprint("content", __name__, template_folder='template', static_folder='static')


@content_.route("/")
def home():
    if flask_login.current_user.is_authenticated:
        files = os.listdir(FILES_LOCATION)

        current_size = f"{str(round(get_current_files_size(FILES_LOCATION) / 1000000000, 2))} GB"
        max_size = f"{MAX_SHARED_FILES_SIZE / 1000000000} GB"

        user_name = flask_login.current_user.id

        can_delete = permissions.can_delete(user_name)
        can_upload = permissions.can_upload(user_name)
        have_private_space = permissions.have_private_space(user_name)

        return render_template("index.html", files=files, max_size=max_size, current_size=current_size,
                               can_delete=can_delete, can_upload=can_upload, have_private_space=have_private_space)
    else:
        return redirect(url_for("auth.login"))


@content_.route("/private")
@flask_login.login_required
def private():
    if flask_login.current_user.have_private_space:
        user_name = flask_login.current_user.id
        check_dir(f"{PRIVATE_FILES_LOCATION}{user_name}")

        files = os.listdir(f"{PRIVATE_FILES_LOCATION}{user_name}")

        max_private_size = permissions.max_private_files_size(user_name)

        current_size = f"{str(round(get_current_files_size(f'{PRIVATE_FILES_LOCATION}{user_name}/') / 1000000000, 2))} GB"
        max_size = f"{max_private_size / 1000000000} GB"

        have_private_space = permissions.have_private_space(user_name)

        return render_template("private.html", files=files, max_size=max_size, current_size=current_size,
                                have_private_space=have_private_space)
    else:
        return redirect(url_for("content.home"))


@content_.route("/upload")
@flask_login.login_required
def upload_view():
    user_name = flask_login.current_user.id

    have_private_space = permissions.have_private_space(user_name)
    can_upload = permissions.can_upload(user_name)

    files = os.listdir(FILES_LOCATION)

    current_size = f"{str(round(get_current_files_size(FILES_LOCATION) / 1000000000, 2))} GB"
    max_size = f"{MAX_SHARED_FILES_SIZE / 1000000000} GB"

    return render_template("upload.html", files=files, max_size=max_size, current_size=current_size,
                               have_private_space=have_private_space, can_upload=can_upload)


@content_.route("/main/upload/finalize/move", methods=["POST", "GET"])
@flask_login.login_required
def move_upload():
    user_name = flask_login.current_user.id
    can_upload = permissions.can_upload(user_name)
    have_private_space = permissions.have_private_space(user_name)

    if can_upload or have_private_space:
        if os.path.exists(f"{TMP_LOCATION}{user_name}/tmp_file"):
            file_name = request.form["file_name"]
            file_name = secure_filename(file_name)

            space = request.form["space"]

            if can_upload and space == "shared":
                if (os.path.getsize(f"{TMP_LOCATION}{user_name}/tmp_file")) + get_current_files_size(
                        FILES_LOCATION) < MAX_SHARED_FILES_SIZE:
                    if not os.path.exists(f"{FILES_LOCATION}{file_name}"):
                        # Handle cross-devide link in docker
                        file_source = open(f"{TMP_LOCATION}{user_name}/tmp_file", "rb")
                        file_dest = open(f"{FILES_LOCATION}{file_name}", "wb")

                        shutil.copyfileobj(file_source, file_dest, 4096)

                        file_source.close()
                        file_dest.close()

                        os.remove(f"{TMP_LOCATION}{user_name}/tmp_file")

                        return redirect(url_for("content.home"))
                    else:
                        message = "File already exists, choose different name"
                        return render_template("finalize.html", have_private_space=have_private_space,
                                               can_upload=can_upload, message=message)
                else:
                    os.remove(f"{TMP_LOCATION}{user_name}/tmp_file")

                    return redirect(url_for("content.home"))

            if have_private_space and space == "private":
                if (os.path.getsize(f"{TMP_LOCATION}{user_name}/tmp_file")) + get_current_files_size(
                        FILES_LOCATION) < MAX_SHARED_FILES_SIZE:
                    if not os.path.exists(f"{PRIVATE_FILES_LOCATION}{user_name}/{file_name}"):
                        # Handle cross-devide link in dockr
                        file_source = open(f"{TMP_LOCATION}{user_name}/tmp_file", "rb")
                        file_dest = open(f"{PRIVATE_FILES_LOCATION}{user_name}/{file_name}", "wb")

                        shutil.copyfileobj(file_source, file_dest, 4096)

                        file_source.close()
                        file_dest.close()

                        os.remove(f"{TMP_LOCATION}{user_name}/tmp_file")

                        return redirect(url_for("content.private"))
                    else:
                        message = "File already exists, choose different name"
                        return render_template("finalize.html", have_private_space=have_private_space,
                                                       can_upload=can_upload, message=message)
                else:
                    os.remove(f"{TMP_LOCATION}{user_name}/tmp_file")

                    return redirect(url_for("content.home"))


@content_.route("/main/upload/finalize", methods=["POST", "GET"])
@flask_login.login_required
def finalize_upload():
    user_name = flask_login.current_user.id
    can_upload = permissions.can_upload(user_name)
    have_private_space = permissions.have_private_space(user_name)

    if can_upload or have_private_space:
        if os.path.exists(f"{TMP_LOCATION}{user_name}/tmp_file"):
            return render_template("finalize.html", have_private_space=have_private_space, can_upload=can_upload,
                                   message="")
        else:
            return redirect(url_for("content.home"))
    else:
        return redirect(url_for("content.home"))


@content_.route("/main/upload", methods=["POST"])
@flask_login.login_required
def upload():
    user_name = flask_login.current_user.id
    can_upload = permissions.can_upload(user_name)
    have_private_space = permissions.have_private_space(user_name)

    if can_upload or have_private_space:
        check_dir(f"{TMP_LOCATION}{user_name}")

        if os.path.exists(f"{TMP_LOCATION}{user_name}/tmp_file"):
            os.remove(f"{TMP_LOCATION}{user_name}/tmp_file")

        if not LEGACY_UPLOAD:
            with open(f"{TMP_LOCATION}{user_name}/tmp_file", "wb") as data:
                while True:
                    file_chunk = request.stream.read(UPLOAD_CHUNK_SIZE)
                    if len(file_chunk) <= 0:
                        break

                    data.write(file_chunk)
        else:
            file = request.files["file-upload"]
            file.save(f"{TMP_LOCATION}{user_name}/tmp_file")

        return redirect(url_for("content.finalize_upload"))

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
    user_name = flask_login.current_user.id
    have_private_space = permissions.have_private_space(user_name)

    if have_private_space:
        if request.args.get("download_file"):
            file_name = request.args.get("download_file")
            return redirect(url_for("content.download_private", file_name=file_name))
        elif request.args.get("delete_file"):
            file_name = request.args.get("delete_file")
            return redirect(url_for("content.delete_private", file_name=file_name))


@content_.route("/main/download_private/<file_name>", methods=["GET"])
@flask_login.login_required
def download_private(file_name):
    user_name = flask_login.current_user.id
    have_private_space = permissions.have_private_space(user_name)

    if have_private_space:
        if file_name.endswith(".pdf")  or file_name.endswith(".txt"):
            return send_file(f"{PRIVATE_FILES_LOCATION}{flask_login.current_user.id}/{file_name}",
                             as_attachment=False, attachment_filename=f'{file_name}', cache_timeout=0)
        else:
            return send_file(f"{PRIVATE_FILES_LOCATION}{flask_login.current_user.id}/{file_name}",
                             as_attachment=True, attachment_filename=f'{file_name}', cache_timeout=0)


@content_.route("/main/delete_private/<file_name>", methods=["GET"])
@flask_login.login_required
def delete_private(file_name):
    user_name = flask_login.current_user.id
    have_private_space = permissions.have_private_space(user_name)

    if have_private_space:
        os.remove(f"{PRIVATE_FILES_LOCATION}{user_name}/{file_name}")

    return redirect(url_for("content.private"))


@content_.route("/main/download/<file_name>", methods=["GET"])
@flask_login.login_required
def download(file_name):
    if file_name.endswith(".pdf")  or file_name.endswith(".txt"):
        return send_file(f'{FILES_LOCATION}{file_name}', as_attachment=False, attachment_filename=f'{file_name}',
                         cache_timeout=0)
    else:
        return send_file(f'{FILES_LOCATION}{file_name}', as_attachment=True, attachment_filename=f'{file_name}',
                         cache_timeout=0)


@content_.route("/main/delete/<file_name>", methods=["GET"])
@flask_login.login_required
def delete(file_name):
    user_name = flask_login.current_user.id
    can_delete_files = permissions.can_delete(user_name)

    if can_delete_files:
        os.remove(f"{FILES_LOCATION}{file_name}")

    return redirect(url_for("content.home"))


@content_.route("/admin/reboot", methods=["GET"])
@flask_login.login_required
def reboot():
    user_name = flask_login.current_user.id

    if permissions.is_admin(user_name):
        os.system("reboot")

        return "Rebooting"
    else:
        return "Not Authorized"


@content_.route("/admin/shutdown", methods=["GET"])
@flask_login.login_required
def shutdown():
    user_name = flask_login.current_user.id

    if permissions.is_admin(user_name):
        os.system("shutdown")

        return "Shutting now"
    else:
        return "Not Authorized"


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