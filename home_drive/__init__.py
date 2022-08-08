from flask import Flask
import flask_login
from flask_sqlalchemy import SQLAlchemy
import os


db = SQLAlchemy()


def register_blueprints(app):
    from home_drive.routes import content, auth, files_operations, errors

    app.register_blueprint(content.content)
    app.register_blueprint(auth.auth)
    app.register_blueprint(files_operations.files_operations)
    app.register_blueprint(errors.errors)


def create_app():
    app = Flask(__name__, instance_relative_config=False)
    app.secret_key = os.urandom(25)
    app.config.from_object('config.Config')
    app.config['MAX_CONTENT_LENGTH'] = app.config["MAX_UPLOAD_SIZE"] * 1024 * 1024

    login_manager = flask_login.LoginManager()
    login_manager.init_app(app)

    db.init_app(app)

    from home_drive import models

    @login_manager.user_loader
    def user_loader(user_id):
        return models.User.query.get(int(user_id))

    with app.app_context():
        db.create_all()

        register_blueprints(app)

        return app
