from flask import render_template, Blueprint, redirect, url_for
from flask import current_app as app
import flask_login


MAX_UPLOAD_SIZE = app.config["MAX_UPLOAD_SIZE"]
FILES_LOCATION = app.config["FILES_LOCATION"]
CURRENT_DIR = app.config["CURRENT_DIR"]
MAX_FILES_SIZE = app.config["MAX_FILES_SIZE"]

app.config['MAX_CONTENT_LENGTH'] = MAX_UPLOAD_SIZE * 1024 * 1024

content_ = Blueprint("content", __name__, template_folder='template', static_folder='static')


@content_.route("/")
def home():
    if flask_login.current_user.is_authenticated:
        return render_template("index.html")
    else:
        return redirect(url_for("auth.login"))


@app.errorhandler(404)
def not_found(error):
    return render_template("error.html", message=error)


@app.errorhandler(500)
def overloaded(error):
    return render_template("error.html", message=error)


@app.errorhandler(401)
def non_authenticated(error):
    return render_template("error.html", message=error)


@app.errorhandler(405)
def method_not_allowed(error):
    return render_template("error.html", message=error)