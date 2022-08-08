from flask import render_template, request, redirect, url_for, Blueprint, flash
import flask_login
from passlib.hash import sha256_crypt
from home_drive.models import User


auth = Blueprint("auth", __name__, template_folder='template', static_folder='static')


@auth.route("/auth/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        if flask_login.current_user.is_authenticated:
            return redirect(url_for("content.home"))

        else:
            return render_template("login.html")

    else:
        try:
            username = request.form["user_name"]
            password = request.form["password"]

            user = User.query.filter_by(username=username).first()

            if user and sha256_crypt.verify(password, user.password):
                flask_login.login_user(user)

                return redirect(url_for("content.home"))

            else:
                flash("Wrong username or password", "error")

                return redirect(url_for("auth.login"))

        except:
            flash("Wrong username or password", "error")

            return redirect(url_for("auth.login"))


@auth.route("/auth/logout", methods=["POST", "GET"])
@flask_login.login_required
def logout():
    flask_login.logout_user()

    return redirect(url_for("content.home"))
