from flask import Flask
import flask_login
from users import User
from users import users_accounts


def create_app():
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object('config.Config')

    login_manager = flask_login.LoginManager()
    login_manager.init_app(app)
    users = users_accounts.UsersAccounts.users

    @login_manager.user_loader
    def user_loader(username):

        if username not in users:
            return

        user = User.User()
        user.id = username
        return user

    with app.app_context():
        from routes import content, auth

        app.register_blueprint(content.content_)
        app.register_blueprint(auth.auth_)

        return app
