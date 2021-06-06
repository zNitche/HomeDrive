from flask import Blueprint
import flask_login
import permissions
import os


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
