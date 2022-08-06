from flask import Flask
import flask_login
from home_drive.users.user import User
from home_drive.users import users_accounts
import permissions
import os


def create_app():
    app = Flask(__name__, instance_relative_config=False)
    app.secret_key = os.urandom(25)
    app.config.from_object('config.Config')
    app.config['MAX_CONTENT_LENGTH'] = app.config["MAX_UPLOAD_SIZE"] * 1024 * 1024

    login_manager = flask_login.LoginManager()
    login_manager.init_app(app)
    users = users_accounts.UsersAccounts.users

    @login_manager.user_loader
    def user_loader(username):

        if username not in users:
            return

        user = User(permissions.can_delete(username), permissions.have_private_space(username),
                         permissions.can_upload(username))
        user.id = username
        return user

    with app.app_context():
        from home_drive.routes import content, auth, files_operations, admin, errors

        app.register_blueprint(content.content_)
        app.register_blueprint(auth.auth_)
        app.register_blueprint(files_operations.files_operations_)
        app.register_blueprint(admin.admin_)
        app.register_blueprint(errors.errors_)

        return app
