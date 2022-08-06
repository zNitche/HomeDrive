from flask import current_app as app
from flask import render_template, url_for, redirect, Blueprint


errors_ = Blueprint("errors", __name__, template_folder='template', static_folder='static')


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
