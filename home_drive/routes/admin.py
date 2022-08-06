from flask import Blueprint, render_template, redirect, url_for
from config import Config
import flask_login
import permissions
import os
from home_drive.utils import get_users


admin_ = Blueprint("admin", __name__, template_folder='template', static_folder='static')


@admin_.route("/admin/reboot", methods=["GET"])
@flask_login.login_required
def reboot():
    user_name = flask_login.current_user.id

    if permissions.is_admin(user_name):
        os.system("reboot")

        return "Rebooting"
    else:
        return "Not Authorized"


@admin_.route("/admin/shutdown", methods=["GET"])
@flask_login.login_required
def shutdown():
    user_name = flask_login.current_user.id

    if permissions.is_admin(user_name):
        os.system("shutdown")

        return "Shutting now"
    else:
        return "Not Authorized"


@admin_.route("/admin/stats")
@flask_login.login_required
def stats():
    user_name = flask_login.current_user.id

    if permissions.is_admin(user_name):
        config = {}
        app_config = dict(vars(Config))

        for key in app_config:
            if not key.startswith("_"):
                config[key] = app_config[key]

        users = get_users()

        return render_template("admin.html", config=config, users=users)
    else:
        return redirect(url_for("content.home"))
