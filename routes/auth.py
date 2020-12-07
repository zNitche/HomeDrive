from flask import render_template, request, redirect, url_for, Blueprint
import flask_login
from users import User
from users import users_accounts as users


auth_ = Blueprint("auth", __name__, template_folder='template', static_folder='static')
