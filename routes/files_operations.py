from flask import render_template, Blueprint, redirect, url_for, request, send_file
import flask_login
from flask import current_app as app
import permissions
from utils import decode_path, get_current_files_size, check_dir
import shutil
import os
from werkzeug.utils import secure_filename


files_operations_ = Blueprint("files_operations", __name__, template_folder='template', static_folder='static')


FILES_LOCATION = app.config["FILES_LOCATION"]
MAX_SHARED_FILES_SIZE = app.config["MAX_SHARED_FILES_SIZE"]
TMP_LOCATION = app.config["TMP_LOCATION"]
PRIVATE_FILES_LOCATION = app.config["PRIVATE_FILES_LOCATION"]
LEGACY_UPLOAD = app.config["LEGACY_UPLOAD"]
UPLOAD_CHUNK_SIZE = app.config["UPLOAD_CHUNK_SIZE"]


@files_operations_.route("/files_operations/download_private/<file_name>", methods=["GET"])
@flask_login.login_required
def download_private(file_name):
    user_name = flask_login.current_user.id
    have_private_space = permissions.have_private_space(user_name)

    if have_private_space:
        file_name = decode_path(file_name)

        if file_name.endswith(".pdf") or file_name.endswith(".txt"):
            return send_file(f"{PRIVATE_FILES_LOCATION}{flask_login.current_user.id}/{file_name}",
                             as_attachment=False, attachment_filename=f'{file_name}', cache_timeout=0)
        else:
            return send_file(f"{PRIVATE_FILES_LOCATION}{flask_login.current_user.id}/{file_name}",
                             as_attachment=True, attachment_filename=f'{file_name}', cache_timeout=0)


@files_operations_.route("/files_operations/delete_private/<file_name>", methods=["GET"])
@flask_login.login_required
def delete_private(file_name):
    user_name = flask_login.current_user.id
    have_private_space = permissions.have_private_space(user_name)

    if have_private_space:
        private_root = f"{PRIVATE_FILES_LOCATION}{user_name}"

        file_name = decode_path(file_name)

        if os.path.isdir(os.path.join(private_root, file_name)):
            shutil.rmtree(os.path.join(private_root, file_name))
        else:
            os.remove(os.path.join(private_root, file_name))

    return redirect(url_for("content.private"))


@files_operations_.route("/files_operations/download/<file_name>", methods=["GET"])
@flask_login.login_required
def download(file_name):
    if file_name.endswith(".pdf") or file_name.endswith(".txt"):
        return send_file(f'{FILES_LOCATION}{file_name}', as_attachment=False, attachment_filename=f'{file_name}',
                         cache_timeout=0)
    else:
        return send_file(f'{FILES_LOCATION}{file_name}', as_attachment=True, attachment_filename=f'{file_name}',
                         cache_timeout=0)


@files_operations_.route("/files_operations/delete/<file_name>", methods=["GET"])
@flask_login.login_required
def delete(file_name):
    user_name = flask_login.current_user.id
    can_delete_files = permissions.can_delete(user_name)

    if can_delete_files:
        os.remove(f"{FILES_LOCATION}{file_name}")

    return redirect(url_for("content.home"))


@files_operations_.route("/files_operations/create_dir/process", methods=["POST"])
@flask_login.login_required
def create_new_directory():
    user_name = flask_login.current_user.id

    if permissions.have_private_space(user_name):
        if request.form["dir_name"]:
            dir_name = request.form["dir_name"]
            path_to_user_files = f"{PRIVATE_FILES_LOCATION}{user_name}"

            files = os.listdir(path_to_user_files)

            if dir_name in files:
                message = "Directory exists"
                return render_template("directory.html", message=message)
            else:
                dir_name = secure_filename(dir_name)

                os.mkdir(os.path.join(path_to_user_files, dir_name))

                return redirect(url_for("content.private"))

        else:
            message = "Directory name can't be empty"
            return render_template("directory.html", message=message)
    else:
        return redirect(url_for("content.home"))


@files_operations_.route("/files_operations/upload/finalize/move", methods=["POST", "GET"])
@flask_login.login_required
def move_upload():
    user_name = flask_login.current_user.id
    can_upload = permissions.can_upload(user_name)
    have_private_space = permissions.have_private_space(user_name)

    if can_upload or have_private_space:
        if os.path.exists(f"{TMP_LOCATION}{user_name}/tmp_file"):
            file_name = secure_filename(request.form["file_name"])
            dir_name = secure_filename(request.form["dirs"])
            space = request.form["space"]

            if can_upload and space == "shared":
                if (os.path.getsize(f"{TMP_LOCATION}{user_name}/tmp_file")) + get_current_files_size(
                        FILES_LOCATION) < MAX_SHARED_FILES_SIZE:
                    if not os.path.exists(f"{FILES_LOCATION}{file_name}"):
                        # Handle cross-device link in docker
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

                    files_root_path = f"{PRIVATE_FILES_LOCATION}{user_name}"

                    if dir_name == "/":
                        dest_path = os.path.join(files_root_path, file_name)
                    else:
                        dest_path = os.path.join(files_root_path, os.path.join(dir_name, file_name))

                    if not os.path.exists(dest_path):
                        # Handle cross-device link in docker
                        file_source = open(f"{TMP_LOCATION}{user_name}/tmp_file", "rb")

                        file_dest = open(dest_path, "wb")

                        shutil.copyfileobj(file_source, file_dest, 4096)

                        file_source.close()
                        file_dest.close()

                        os.remove(f"{TMP_LOCATION}{user_name}/tmp_file")

                        return redirect(url_for("content.private"))
                    else:
                        message = "File already exists, choose different name"
                        dirs = ["/"]

                        objects = os.listdir(files_root_path)
                        for obj in objects:
                            if os.path.isdir(os.path.join(files_root_path, obj)):
                                dirs.append(obj)

                        return render_template("finalize.html", have_private_space=have_private_space,
                                                       can_upload=can_upload, message=message, dirs=dirs)
                else:
                    os.remove(f"{TMP_LOCATION}{user_name}/tmp_file")

                    return redirect(url_for("content.home"))


@files_operations_.route("/files_operations/upload/finalize", methods=["POST", "GET"])
@flask_login.login_required
def finalize_upload():
    user_name = flask_login.current_user.id
    can_upload = permissions.can_upload(user_name)
    have_private_space = permissions.have_private_space(user_name)

    if can_upload or have_private_space:
        objects_root = f"{PRIVATE_FILES_LOCATION}{user_name}"
        objects = os.listdir(objects_root)
        dirs = ["/"]

        for obj in objects:
            if os.path.isdir(os.path.join(objects_root, obj)):
                dirs.append(obj)

        if os.path.exists(f"{TMP_LOCATION}{user_name}/tmp_file"):
            return render_template("finalize.html", have_private_space=have_private_space, can_upload=can_upload,
                                   message="", dirs=dirs)
        else:
            return redirect(url_for("content.home"))
    else:
        return redirect(url_for("content.home"))


@files_operations_.route("/files_operations/upload", methods=["POST"])
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

        return redirect(url_for("files_operations.finalize_upload"))

    else:
        return redirect(url_for("content.home"))


@files_operations_.route("/files_operations/move/process", methods=["POST"])
@flask_login.login_required
def move_file_process():
    #TODO rework this one
    user_name = flask_login.current_user.id

    if permissions.have_private_space(user_name):
        objects_path = f"{PRIVATE_FILES_LOCATION}{user_name}"

        dirs = ["/"]
        objects = os.listdir(objects_path)

        for obj in objects:
            if os.path.isdir(os.path.join(objects_path, obj)):
                dirs.append(obj)

        if request.form["dirs"]:
            objects_root = f"{PRIVATE_FILES_LOCATION}{user_name}"

            dest_dir = request.form["dirs"]
            file_name = request.form["file_name"]
            file_name = decode_path(file_name)

            decoded_name_splited = file_name.split("/")

            if not dest_dir == "/":
                dest_dir = secure_filename(dest_dir)

            if len(decoded_name_splited) < 2:
                file_name = file_name.split("/")[0]

                file_name = secure_filename(file_name)

                file_path = os.path.join(objects_root, file_name)
                dest_path = os.path.join(dest_dir, file_name)
                dest_path = f"{objects_root}/{dest_path}"
            else:
                file_dir = file_name.split("/")[0]
                file_name = file_name.split("/")[1]

                file_name = secure_filename(file_name)
                file_dir = secure_filename(file_dir)

                file_path = os.path.join(objects_root, os.path.join(file_dir, file_name))
                dest_path = os.path.join(dest_dir, file_name)
                dest_path = f"{objects_root}/{dest_path}"

            shutil.move(file_path, dest_path)

            return redirect(url_for("content.private"))
        else:
            message = "choose directory first"
            return render_template("move_file.html", message=message)
    else:
        return redirect(url_for("content.home"))
